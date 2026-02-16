from fastapi import APIRouter, HTTPException, Query, Depends
from bson import ObjectId
from datetime import datetime
from database import get_db
from models import BlogPostCreate, PaginatedResponse
from auth import get_current_admin
from math import ceil
import re

router = APIRouter(prefix="/api/blog", tags=["blog"])

def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    # Convert to lowercase
    slug = title.lower().strip()
    # Replace Cyrillic and other characters with transliteration where possible
    # For simplicity, just remove non-ASCII and replace spaces
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug

async def ensure_unique_slug(db, slug: str, exclude_id: str = None) -> str:
    """Ensure slug is unique, adding suffix if needed"""
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

async def record_view(db, entity_type: str, entity_id: str):
    """Record view in daily stats"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    await db.view_records.update_one(
        {"entity_type": entity_type, "entity_id": entity_id, "date": today},
        {"$inc": {"count": 1}, "$setOnInsert": {"entity_type": entity_type, "entity_id": entity_id, "date": today}},
        upsert=True
    )
    
    await db.daily_views.update_one(
        {"entity_type": entity_type, "date": today},
        {"$inc": {"count": 1}, "$setOnInsert": {"entity_type": entity_type, "date": today}},
        upsert=True
    )

@router.get("")
async def get_posts(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100), 
    search: str = Query(""), 
    sort: str = Query("newest")  # newest, oldest, views
):
    db = get_db()
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}}, 
            {"content": {"$regex": search, "$options": "i"}}
        ]
    
    # Determine sort field and order
    if sort == "newest":
        sort_field = "created_at"
        sort_order = -1
    elif sort == "oldest":
        sort_field = "created_at"
        sort_order = 1
    elif sort == "views":
        sort_field = "views"
        sort_order = -1
    else:
        sort_field = "created_at"
        sort_order = -1
    
    skip = (page - 1) * limit
    total = await db.blog.count_documents(query)
    cursor = db.blog.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
    items = [serialize(dict(doc)) async for doc in cursor]
    pages = ceil(total / limit) if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, pages=pages, has_next=page < pages, has_prev=page > 1)

@router.get("/by-slug/{slug}")
async def get_post_by_slug(slug: str):
    """Get post by slug"""
    db = get_db()
    post = await db.blog.find_one({"slug": slug})
    if not post:
        raise HTTPException(status_code=404, detail="Not found")
    
    return serialize(dict(post))

@router.get("/{post_id}")
async def get_post(post_id: str):
    db = get_db()
    
    # Try to find by ID first
    if ObjectId.is_valid(post_id):
        post = await db.blog.find_one({"_id": ObjectId(post_id)})
    else:
        # Try by slug
        post = await db.blog.find_one({"slug": post_id})
    
    if not post:
        raise HTTPException(status_code=404, detail="Not found")
    
    return serialize(dict(post))

@router.post("")
async def create_post(post: BlogPostCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    doc = post.model_dump()
    
    # Generate slug if not provided
    if not doc.get("slug"):
        doc["slug"] = generate_slug(doc["title"])
    
    # Ensure unique slug
    doc["slug"] = await ensure_unique_slug(db, doc["slug"])
    
    doc["created_at"] = datetime.utcnow()
    doc["views"] = 0
    result = await db.blog.insert_one(doc)
    created = await db.blog.find_one({"_id": result.inserted_id})
    return serialize(dict(created))

@router.put("/{post_id}")
async def update_post(post_id: str, post: BlogPostCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    data = post.model_dump()
    
    # Generate slug if not provided
    if not data.get("slug"):
        data["slug"] = generate_slug(data["title"])
    
    # Ensure unique slug (excluding current post)
    data["slug"] = await ensure_unique_slug(db, data["slug"], post_id)
    
    result = await db.blog.update_one({"_id": ObjectId(post_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = await db.blog.find_one({"_id": ObjectId(post_id)})
    return serialize(dict(updated))

@router.delete("/{post_id}")
async def delete_post(post_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.blog.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}
