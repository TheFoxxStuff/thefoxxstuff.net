import logging
from math import ceil
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends, Response

from database import get_db
from models import BlogPostCreate, PaginatedResponse
from auth import get_current_admin
from cache import cache_get_or_set, cache_delete_pattern
from config import settings
from utils import generate_slug

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/blog", tags=["blog"])


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
    while await db.blog.find_one(query):
        slug = f"{base_slug}-{counter}"
        query["slug"] = slug
        counter += 1
    return slug


async def _invalidate():
    await cache_delete_pattern("blog:*")


async def enrich_post(db, post: dict) -> dict:
    """Обогащает один пост данными cover_image_info и og_image_info."""
    from bson import ObjectId
    for field, info_field in [("cover_image", "cover_image_info"), ("og_image", "og_image_info")]:
        val = post.get(field)
        if val and ObjectId.is_valid(val):
            img = await db.images.find_one({"_id": ObjectId(val)})
            if img:
                post[info_field] = serialize(dict(img))
    return post


async def enrich_posts_batch(db, posts: list) -> list:
    """N+1 fix: загружает все обложки постов одним $in запросом."""
    from bson import ObjectId
    cover_ids = [
        ObjectId(p["cover_image"]) for p in posts
        if p.get("cover_image") and ObjectId.is_valid(p["cover_image"])
    ]
    images_map = {}
    if cover_ids:
        async for img in db.images.find({"_id": {"$in": cover_ids}}):
            images_map[str(img["_id"])] = serialize(dict(img))

    for post in posts:
        cid = post.get("cover_image")
        if cid and cid in images_map:
            post["cover_image_info"] = images_map[cid]

    return posts


# ─── GET (cached + Cache-Control) ────────────────────────────────────────────

@router.get("")
async def get_posts(
    response: Response,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(""),
    sort: str = Query("newest"),
):
    # Поисковые запросы не кэшируем в браузере
    if search:
        response.headers["Cache-Control"] = "no-cache"
    else:
        response.headers["Cache-Control"] = "public, max-age=30, stale-while-revalidate=60"

    key = f"blog:list:{page}:{limit}:{search}:{sort}"
    ttl = 15 if search else settings.cache_ttl_list

    async def fetch():
        db = get_db()
        query = {}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"content": {"$regex": search, "$options": "i"}},
            ]
        sort_map = {"newest": ("created_at", -1), "oldest": ("created_at", 1), "views": ("views", -1)}
        sort_field, sort_order = sort_map.get(sort, ("created_at", -1))
        skip = (page - 1) * limit
        total = await db.blog.count_documents(query)
        cursor = db.blog.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        items = [serialize(dict(doc)) async for doc in cursor]
        items = await enrich_posts_batch(db, items)  # N+1 fix
        pages = ceil(total / limit) if total > 0 else 1
        return PaginatedResponse(
            items=items, total=total, page=page, pages=pages,
            has_next=page < pages, has_prev=page > 1,
        ).model_dump()

    return await cache_get_or_set(key, fetch, ttl)


@router.get("/by-slug/{slug}")
async def get_post_by_slug(slug: str, response: Response):
    response.headers["Cache-Control"] = "public, max-age=60"

    async def fetch():
        db = get_db()
        post = await db.blog.find_one({"slug": slug})
        if not post:
            return None
        post = serialize(dict(post))
        return await enrich_post(db, post)

    result = await cache_get_or_set(f"blog:item:slug:{slug}", fetch, settings.cache_ttl_item)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/{post_id}")
async def get_post(post_id: str, response: Response):
    response.headers["Cache-Control"] = "public, max-age=60"

    async def fetch():
        db = get_db()
        if ObjectId.is_valid(post_id):
            post = await db.blog.find_one({"_id": ObjectId(post_id)})
        else:
            post = await db.blog.find_one({"slug": post_id})
        if not post:
            return None
        post = serialize(dict(post))
        return await enrich_post(db, post)

    result = await cache_get_or_set(f"blog:item:{post_id}", fetch, settings.cache_ttl_item)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return result


# ─── Mutations ────────────────────────────────────────────────────────────────

@router.post("")
async def create_post(post: BlogPostCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    doc = post.model_dump()
    if not doc.get("slug"):
        doc["slug"] = generate_slug(doc["title"])
    doc["slug"] = await ensure_unique_slug(db, doc["slug"])
    doc["created_at"] = datetime.utcnow()
    doc["views"] = 0
    result = await db.blog.insert_one(doc)
    created = serialize(dict(await db.blog.find_one({"_id": result.inserted_id})))
    await _invalidate()
    return created


@router.put("/{post_id}")
async def update_post(post_id: str, post: BlogPostCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    data = post.model_dump()
    if not data.get("slug"):
        data["slug"] = generate_slug(data["title"])
    data["slug"] = await ensure_unique_slug(db, data["slug"], post_id)
    result = await db.blog.update_one({"_id": ObjectId(post_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = serialize(dict(await db.blog.find_one({"_id": ObjectId(post_id)})))
    await _invalidate()
    return updated


@router.delete("/{post_id}")
async def delete_post(post_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    # Get post to find associated images
    post = await db.blog.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Not found")

    # Collect image IDs to potentially cleanup
    image_ids = []
    if post.get("cover_image"):
        image_ids.append(post["cover_image"])
    if post.get("og_image"):
        image_ids.append(post["og_image"])

    # Delete the post
    result = await db.blog.delete_one({"_id": ObjectId(post_id)})

    # Mark images as potentially orphaned
    if image_ids:
        await db.images.update_many(
            {"_id": {"$in": [ObjectId(id) for id in image_ids if ObjectId.is_valid(id)]}},
            {"$set": {"parent_deleted": True, "parent_deleted_at": datetime.utcnow()}}
        )

    await _invalidate()
    return {"deleted": True, "orphaned_images": len(image_ids)}
