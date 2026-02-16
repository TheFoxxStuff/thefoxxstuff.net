from fastapi import APIRouter, HTTPException, Query, Depends
from bson import ObjectId
from datetime import datetime
from database import get_db
from models import MusicReleaseCreate, PaginatedResponse
from auth import get_current_admin
from math import ceil
import re

router = APIRouter(prefix="/api/music", tags=["music"])

def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = title.lower().strip()
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
    
    while await db.music.find_one(query):
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

async def enrich_with_images(db, release):
    """Add image info to release"""
    if release.get("cover_image") and ObjectId.is_valid(release["cover_image"]):
        image = await db.images.find_one({"_id": ObjectId(release["cover_image"])})
        if image:
            release["cover_image_info"] = serialize(dict(image))
    
    if release.get("gallery"):
        gallery_images = []
        for g in release["gallery"]:
            # Handle both old format (string ID) and new format (dict with image_id and name)
            if isinstance(g, dict):
                img_id = g.get("image_id")
                name = g.get("name", "")
            else:
                img_id = g
                name = ""
            
            if img_id and ObjectId.is_valid(img_id):
                image = await db.images.find_one({"_id": ObjectId(img_id)})
                if image:
                    img_info = serialize(dict(image))
                    img_info["gallery_name"] = name
                    gallery_images.append(img_info)
        release["gallery_images"] = gallery_images
    
    return release

@router.get("")
async def get_releases(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    db = get_db()
    skip = (page - 1) * limit
    total = await db.music.count_documents({})
    cursor = db.music.find().sort("release_date", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        release = serialize(dict(doc))
        release = await enrich_with_images(db, release)
        items.append(release)
    pages = ceil(total / limit) if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, pages=pages, has_next=page < pages, has_prev=page > 1)

@router.get("/featured")
async def get_featured():
    db = get_db()
    release = await db.music.find_one({"is_new": True}, sort=[("release_date", -1)])
    if not release:
        release = await db.music.find_one(sort=[("release_date", -1)])
    if release:
        release = serialize(dict(release))
        release = await enrich_with_images(db, release)
    return release

@router.get("/by-slug/{slug}")
async def get_release_by_slug(slug: str):
    """Get release by slug"""
    db = get_db()
    release = await db.music.find_one({"slug": slug})
    if not release:
        raise HTTPException(status_code=404, detail="Not found")
    
    release = serialize(dict(release))
    release = await enrich_with_images(db, release)
    return release

@router.get("/{release_id}")
async def get_release(release_id: str):
    db = get_db()
    
    # Try to find by ID first
    if ObjectId.is_valid(release_id):
        release = await db.music.find_one({"_id": ObjectId(release_id)})
    else:
        # Try by slug
        release = await db.music.find_one({"slug": release_id})
    
    if not release:
        raise HTTPException(status_code=404, detail="Not found")
    
    release = serialize(dict(release))
    release = await enrich_with_images(db, release)
    return release

@router.post("")
async def create_release(release: MusicReleaseCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    doc = release.model_dump()
    
    # Convert tracks to dicts if they're TrackItem objects
    if doc.get("tracks"):
        doc["tracks"] = [t if isinstance(t, dict) else t.model_dump() for t in doc["tracks"]]
    
    # Convert gallery to dicts if they're GalleryImage objects
    if doc.get("gallery"):
        doc["gallery"] = [g if isinstance(g, dict) else g.model_dump() for g in doc["gallery"]]
    
    # Generate slug if not provided
    if not doc.get("slug"):
        doc["slug"] = generate_slug(doc["title"])
    
    # Ensure unique slug
    doc["slug"] = await ensure_unique_slug(db, doc["slug"])
    
    doc["views"] = 0
    doc["created_at"] = datetime.utcnow()
    result = await db.music.insert_one(doc)
    created = await db.music.find_one({"_id": result.inserted_id})
    created = serialize(dict(created))
    created = await enrich_with_images(db, created)
    return created

@router.put("/{release_id}")
async def update_release(release_id: str, release: MusicReleaseCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(release_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    data = release.model_dump()
    
    # Convert tracks to dicts if they're TrackItem objects
    if data.get("tracks"):
        data["tracks"] = [t if isinstance(t, dict) else t.model_dump() for t in data["tracks"]]
    
    # Convert gallery to dicts if they're GalleryImage objects
    if data.get("gallery"):
        data["gallery"] = [g if isinstance(g, dict) else g.model_dump() for g in data["gallery"]]
    
    # Generate slug if not provided
    if not data.get("slug"):
        data["slug"] = generate_slug(data["title"])
    
    # Ensure unique slug (excluding current release)
    data["slug"] = await ensure_unique_slug(db, data["slug"], release_id)
    
    result = await db.music.update_one({"_id": ObjectId(release_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = await db.music.find_one({"_id": ObjectId(release_id)})
    updated = serialize(dict(updated))
    updated = await enrich_with_images(db, updated)
    return updated

@router.delete("/{release_id}")
async def delete_release(release_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(release_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.music.delete_one({"_id": ObjectId(release_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}
