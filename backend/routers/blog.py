import logging
import re
from math import ceil
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends

from database import get_db
from models import BlogPostCreate, PaginatedResponse
from auth import get_current_admin
from cache import cache_get, cache_set, cache_delete_pattern
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/blog", tags=["blog"])


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
    while await db.blog.find_one(query):
        slug = f"{base_slug}-{counter}"
        query["slug"] = slug
        counter += 1
    return slug


async def _invalidate():
    await cache_delete_pattern("blog:*")


# ─── GET (cached) ─────────────────────────────────────────────────────────────

@router.get("")
async def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(""),
    sort: str = Query("newest"),
):
    key = f"blog:list:{page}:{limit}:{search}:{sort}"
    cached = await cache_get(key)
    if cached is not None:
        return cached

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
    pages = ceil(total / limit) if total > 0 else 1
    result = PaginatedResponse(
        items=items, total=total, page=page, pages=pages,
        has_next=page < pages, has_prev=page > 1,
    ).model_dump()

    # Only cache non-search queries to avoid bloating Redis
    ttl = settings.cache_ttl_list if not search else 15
    await cache_set(key, result, ttl)
    return result


@router.get("/by-slug/{slug}")
async def get_post_by_slug(slug: str):
    key = f"blog:item:slug:{slug}"
    cached = await cache_get(key)
    if cached is not None:
        return cached

    db = get_db()
    post = await db.blog.find_one({"slug": slug})
    if not post:
        raise HTTPException(status_code=404, detail="Not found")
    result = serialize(dict(post))
    await cache_set(key, result, settings.cache_ttl_item)
    return result


@router.get("/{post_id}")
async def get_post(post_id: str):
    key = f"blog:item:{post_id}"
    cached = await cache_get(key)
    if cached is not None:
        return cached

    db = get_db()
    if ObjectId.is_valid(post_id):
        post = await db.blog.find_one({"_id": ObjectId(post_id)})
    else:
        post = await db.blog.find_one({"slug": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Not found")
    result = serialize(dict(post))
    await cache_set(key, result, settings.cache_ttl_item)
    return result


# ─── Mutations (invalidate) ───────────────────────────────────────────────────

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
    result = await db.blog.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    await _invalidate()
    return {"deleted": True}
