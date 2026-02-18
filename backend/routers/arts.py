import logging
import re
from math import ceil
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends, Response

from database import get_db
from models import ArtWorkCreate, PaginatedResponse
from auth import get_current_admin
from cache import cache_get_or_set, cache_delete_pattern
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/arts", tags=["arts"])


def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def generate_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


async def ensure_unique_slug(db, slug: str, exclude_id: str = None) -> str:
    base_slug = slug
    counter = 1
    query = {"slug": slug}
    if exclude_id:
        query["_id"] = {"$ne": ObjectId(exclude_id)}
    while await db.arts.find_one(query):
        slug = f"{base_slug}-{counter}"
        query["slug"] = slug
        counter += 1
    return slug


async def enrich_artworks_batch(db, artworks: list) -> list:
    """N+1 fix: загружает все изображения для списка артов одним $in запросом."""
    image_ids = [
        ObjectId(a["image"]) for a in artworks
        if a.get("image") and ObjectId.is_valid(a["image"])
    ]
    images_map = {}
    if image_ids:
        async for img in db.images.find({"_id": {"$in": image_ids}}):
            images_map[str(img["_id"])] = serialize(dict(img))

    for artwork in artworks:
        img_id = artwork.get("image")
        if img_id and img_id in images_map:
            artwork["image_info"] = images_map[img_id]

    return artworks


async def enrich_with_image(db, artwork):
    """Для одного элемента."""
    if artwork.get("image") and ObjectId.is_valid(artwork["image"]):
        image = await db.images.find_one({"_id": ObjectId(artwork["image"])})
        if image:
            artwork["image_info"] = serialize(dict(image))
    return artwork


async def _invalidate():
    await cache_delete_pattern("arts:*")


# ─── GET (cached + Cache-Control) ────────────────────────────────────────────

@router.get("")
async def get_artworks(
    response: Response,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    year: int = Query(None),
    sort: str = Query("newest"),
):
    response.headers["Cache-Control"] = "public, max-age=30, stale-while-revalidate=60"
    key = f"arts:list:{page}:{limit}:{year}:{sort}"

    async def fetch():
        db = get_db()
        query = {}
        if year:
            query["year"] = year
        sort_map = {"newest": ("created_at", -1), "oldest": ("created_at", 1), "views": ("views", -1)}
        sort_field, sort_order = sort_map.get(sort, ("created_at", -1))
        skip = (page - 1) * limit
        total = await db.arts.count_documents(query)
        cursor = db.arts.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        items = [serialize(dict(doc)) async for doc in cursor]
        items = await enrich_artworks_batch(db, items)   # N+1 fix
        pages = ceil(total / limit) if total > 0 else 1
        return PaginatedResponse(
            items=items, total=total, page=page, pages=pages,
            has_next=page < pages, has_prev=page > 1,
        ).model_dump()

    return await cache_get_or_set(key, fetch, settings.cache_ttl_list)


@router.get("/years")
async def get_years(response: Response):
    response.headers["Cache-Control"] = "public, max-age=120"

    async def fetch():
        db = get_db()
        return sorted(await db.arts.distinct("year"), reverse=True)

    return await cache_get_or_set("arts:years", fetch, settings.cache_ttl_list)


@router.get("/grouped")
async def get_grouped_artworks(response: Response, limit_per_year: int = Query(7)):
    response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=120"
    key = f"arts:grouped:{limit_per_year}"

    async def fetch():
        db = get_db()
        years = sorted(await db.arts.distinct("year"), reverse=True)
        result = {}
        for year in years:
            cursor = db.arts.find({"year": year}).sort("created_at", -1).limit(limit_per_year)
            artworks = [serialize(dict(doc)) async for doc in cursor]
            artworks = await enrich_artworks_batch(db, artworks)  # N+1 fix
            result[str(year)] = artworks
        return result

    return await cache_get_or_set(key, fetch, settings.cache_ttl_list)


@router.get("/by-slug/{slug}")
async def get_artwork_by_slug(slug: str, response: Response):
    response.headers["Cache-Control"] = "public, max-age=60"

    async def fetch():
        db = get_db()
        artwork = await db.arts.find_one({"slug": slug})
        if not artwork:
            return None
        artwork = serialize(dict(artwork))
        return await enrich_with_image(db, artwork)

    result = await cache_get_or_set(f"arts:item:slug:{slug}", fetch, settings.cache_ttl_item)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/{artwork_id}")
async def get_artwork(artwork_id: str, response: Response):
    response.headers["Cache-Control"] = "public, max-age=60"

    async def fetch():
        db = get_db()
        if ObjectId.is_valid(artwork_id):
            artwork = await db.arts.find_one({"_id": ObjectId(artwork_id)})
        else:
            artwork = await db.arts.find_one({"slug": artwork_id})
        if not artwork:
            return None
        artwork = serialize(dict(artwork))
        return await enrich_with_image(db, artwork)

    result = await cache_get_or_set(f"arts:item:{artwork_id}", fetch, settings.cache_ttl_item)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return result


# ─── Mutations ────────────────────────────────────────────────────────────────

@router.post("")
async def create_artwork(artwork: ArtWorkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    doc = artwork.model_dump()
    if not doc.get("slug"):
        doc["slug"] = generate_slug(doc["title"])
    doc["slug"] = await ensure_unique_slug(db, doc["slug"])
    doc["created_at"] = datetime.utcnow()
    doc["views"] = 0
    result = await db.arts.insert_one(doc)
    created = serialize(dict(await db.arts.find_one({"_id": result.inserted_id})))
    created = await enrich_with_image(db, created)
    await _invalidate()
    return created


@router.put("/{artwork_id}")
async def update_artwork(artwork_id: str, artwork: ArtWorkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(artwork_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    data = artwork.model_dump()
    if not data.get("slug"):
        data["slug"] = generate_slug(data["title"])
    data["slug"] = await ensure_unique_slug(db, data["slug"], artwork_id)
    result = await db.arts.update_one({"_id": ObjectId(artwork_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = serialize(dict(await db.arts.find_one({"_id": ObjectId(artwork_id)})))
    updated = await enrich_with_image(db, updated)
    await _invalidate()
    return updated


@router.delete("/{artwork_id}")
async def delete_artwork(artwork_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(artwork_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.arts.delete_one({"_id": ObjectId(artwork_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    await _invalidate()
    return {"deleted": True}
