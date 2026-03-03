import logging
from math import ceil
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends, Response

from database import get_db
from models import MusicReleaseCreate, PaginatedResponse
from auth import get_current_admin
from cache import cache_delete_pattern, cache_get_or_set
from config import settings
from utils import generate_slug

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/music", tags=["music"])


def _list_key(page: int, limit: int) -> str:
    return f"music:list:{page}:{limit}"

def _item_key(ident: str) -> str:
    return f"music:item:{ident}"

def _featured_key() -> str:
    return "music:featured"


def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def ensure_unique_slug(db, slug: str, exclude_id: str = None) -> str:
    base_slug = slug
    counter = 1
    query = {"slug": slug}
    if exclude_id:
        query["_id"] = {"$ne": ObjectId(exclude_id)}
    while await db.music.find_one(query):
        slug = f"{base_slug}-{counter}"
        query["slug"] = slug
        counter += 1
    return slug


async def enrich_with_images(db, release):
    """Обогащает один релиз данными изображений включая og_image и gallery."""
    # Collect all image IDs we need to fetch
    image_ids = []

    # Cover and OG images
    for field in ["cover_image", "og_image"]:
        val = release.get(field)
        if val and ObjectId.is_valid(val):
            image_ids.append(ObjectId(val))

    # Gallery images
    if release.get("gallery"):
        for g in release["gallery"]:
            if isinstance(g, dict):
                img_id = g.get("image_id")
            else:
                img_id = g
            if img_id and ObjectId.is_valid(img_id):
                image_ids.append(ObjectId(img_id))

    # Fetch all images in one query
    images_map = {}
    if image_ids:
        async for img in db.images.find({"_id": {"$in": image_ids}}):
            images_map[str(img["_id"])] = serialize(dict(img))

    # Assign cover and OG images
    for field, info_field in [
        ("cover_image", "cover_image_info"),
        ("og_image", "og_image_info"),
    ]:
        val = release.get(field)
        if val and val in images_map:
            release[info_field] = images_map[val]

    # Assign gallery images
    if release.get("gallery"):
        gallery_images = []
        for g in release["gallery"]:
            if isinstance(g, dict):
                img_id, name = g.get("image_id"), g.get("name", "")
            else:
                img_id, name = g, ""
            if img_id and img_id in images_map:
                img_info = images_map[img_id]
                img_info["gallery_name"] = name
                gallery_images.append(img_info)
        release["gallery_images"] = gallery_images

    return release


async def enrich_releases_batch(db, releases: list) -> list:
    """
    N+1 fix: загружает все изображения (обложки, OG, gallery) одним $in запросом.
    """
    # Collect all image IDs from all releases
    image_ids = set()

    for r in releases:
        # Cover images
        if r.get("cover_image") and ObjectId.is_valid(r["cover_image"]):
            image_ids.add(ObjectId(r["cover_image"]))

        # OG images
        if r.get("og_image") and ObjectId.is_valid(r["og_image"]):
            image_ids.add(ObjectId(r["og_image"]))

        # Gallery images
        if r.get("gallery"):
            for g in r["gallery"]:
                if isinstance(g, dict):
                    img_id = g.get("image_id")
                else:
                    img_id = g
                if img_id and ObjectId.is_valid(img_id):
                    image_ids.add(ObjectId(img_id))

    # Fetch all images in one query
    images_map = {}
    if image_ids:
        async for img in db.images.find({"_id": {"$in": list(image_ids)}}):
            images_map[str(img["_id"])] = serialize(dict(img))

    # Enrich each release
    for release in releases:
        # Cover image
        cid = release.get("cover_image")
        if cid and cid in images_map:
            release["cover_image_info"] = images_map[cid]

        # OG image
        ogid = release.get("og_image")
        if ogid and ogid in images_map:
            release["og_image_info"] = images_map[ogid]

        # Gallery images
        if release.get("gallery"):
            gallery_images = []
            for g in release["gallery"]:
                if isinstance(g, dict):
                    img_id, name = g.get("image_id"), g.get("name", "")
                else:
                    img_id, name = g, ""
                if img_id and img_id in images_map:
                    img_info = dict(images_map[img_id])
                    img_info["gallery_name"] = name
                    gallery_images.append(img_info)
            release["gallery_images"] = gallery_images

    return releases


async def _invalidate():
    deleted = await cache_delete_pattern("music:*")
    logger.debug("Invalidated %d music cache keys", deleted)


# ─── GET (cached + Cache-Control) ────────────────────────────────────────────

@router.get("")
async def get_releases(
    response: Response,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    response.headers["Cache-Control"] = f"public, max-age=30, stale-while-revalidate=60"

    key = _list_key(page, limit)

    async def fetch():
        db = get_db()
        skip = (page - 1) * limit
        total = await db.music.count_documents({})
        cursor = db.music.find().sort("release_date", -1).skip(skip).limit(limit)
        items = [serialize(dict(doc)) async for doc in cursor]
        items = await enrich_releases_batch(db, items)
        pages = ceil(total / limit) if total > 0 else 1
        return PaginatedResponse(
            items=items, total=total, page=page, pages=pages,
            has_next=page < pages, has_prev=page > 1,
        ).model_dump()

    return await cache_get_or_set(key, fetch, settings.cache_ttl_list)


@router.get("/featured")
async def get_featured(response: Response):
    response.headers["Cache-Control"] = f"public, max-age=60, stale-while-revalidate=120"

    async def fetch():
        db = get_db()
        release = await db.music.find_one({"is_new": True}, sort=[("release_date", -1)])
        if not release:
            release = await db.music.find_one(sort=[("release_date", -1)])
        if release:
            release = serialize(dict(release))
            release = await enrich_with_images(db, release)
        return release

    return await cache_get_or_set(_featured_key(), fetch, settings.cache_ttl_item)


@router.get("/by-slug/{slug}")
async def get_release_by_slug(slug: str, response: Response):
    response.headers["Cache-Control"] = f"public, max-age=60"

    async def fetch():
        db = get_db()
        release = await db.music.find_one({"slug": slug})
        if not release:
            return None
        release = serialize(dict(release))
        return await enrich_with_images(db, release)

    result = await cache_get_or_set(_item_key(f"slug:{slug}"), fetch, settings.cache_ttl_item)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/{release_id}")
async def get_release(release_id: str, response: Response):
    response.headers["Cache-Control"] = "public, max-age=60"

    async def fetch():
        db = get_db()
        if ObjectId.is_valid(release_id):
            release = await db.music.find_one({"_id": ObjectId(release_id)})
        else:
            release = await db.music.find_one({"slug": release_id})
        if not release:
            return None
        release = serialize(dict(release))
        return await enrich_with_images(db, release)

    result = await cache_get_or_set(_item_key(release_id), fetch, settings.cache_ttl_item)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return result


# ─── Mutations ────────────────────────────────────────────────────────────────

@router.post("")
async def create_release(release: MusicReleaseCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    doc = release.model_dump()
    if doc.get("tracks"):
        doc["tracks"] = [t if isinstance(t, dict) else t.model_dump() for t in doc["tracks"]]
    if doc.get("gallery"):
        doc["gallery"] = [g if isinstance(g, dict) else g.model_dump() for g in doc["gallery"]]
    if not doc.get("slug"):
        doc["slug"] = generate_slug(doc["title"])
    doc["slug"] = await ensure_unique_slug(db, doc["slug"])
    doc["views"] = 0
    doc["created_at"] = datetime.utcnow()
    result = await db.music.insert_one(doc)
    created = serialize(dict(await db.music.find_one({"_id": result.inserted_id})))
    created = await enrich_with_images(db, created)
    await _invalidate()
    return created


@router.put("/{release_id}")
async def update_release(release_id: str, release: MusicReleaseCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(release_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    data = release.model_dump()
    if data.get("tracks"):
        data["tracks"] = [t if isinstance(t, dict) else t.model_dump() for t in data["tracks"]]
    if data.get("gallery"):
        data["gallery"] = [g if isinstance(g, dict) else g.model_dump() for g in data["gallery"]]
    if not data.get("slug"):
        data["slug"] = generate_slug(data["title"])
    data["slug"] = await ensure_unique_slug(db, data["slug"], release_id)
    result = await db.music.update_one({"_id": ObjectId(release_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = serialize(dict(await db.music.find_one({"_id": ObjectId(release_id)})))
    updated = await enrich_with_images(db, updated)
    await _invalidate()
    return updated


@router.delete("/{release_id}")
async def delete_release(release_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(release_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    # Get release to find associated images
    release = await db.music.find_one({"_id": ObjectId(release_id)})
    if not release:
        raise HTTPException(status_code=404, detail="Not found")

    # Collect image IDs to potentially cleanup
    image_ids = []
    if release.get("cover_image"):
        image_ids.append(release["cover_image"])
    if release.get("og_image"):
        image_ids.append(release["og_image"])
    if release.get("gallery"):
        for g in release["gallery"]:
            if isinstance(g, dict):
                img_id = g.get("image_id")
            else:
                img_id = g
            if img_id:
                image_ids.append(img_id)

    # Delete the release
    result = await db.music.delete_one({"_id": ObjectId(release_id)})

    # Mark images as potentially orphaned (don't delete immediately - they might be used elsewhere)
    # This is safer than immediate deletion
    if image_ids:
        await db.images.update_many(
            {"_id": {"$in": [ObjectId(id) for id in image_ids if ObjectId.is_valid(id)]}},
            {"$set": {"parent_deleted": True, "parent_deleted_at": datetime.utcnow()}}
        )

    await _invalidate()
    return {"deleted": True, "orphaned_images": len(image_ids)}
