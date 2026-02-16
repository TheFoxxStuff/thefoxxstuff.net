from fastapi import APIRouter, HTTPException, Query, Depends
from bson import ObjectId
from datetime import datetime
from database import get_db
from models import ArtWorkCreate, PaginatedResponse
from auth import get_current_admin
from math import ceil
import re

router = APIRouter(prefix="/api/arts", tags=["arts"])

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
    
    while await db.arts.find_one(query):
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

async def enrich_with_image(db, artwork):
    """Add image info to artwork"""
    if artwork.get("image") and ObjectId.is_valid(artwork["image"]):
        image = await db.images.find_one({"_id": ObjectId(artwork["image"])})
        if image:
            artwork["image_info"] = serialize(dict(image))
    return artwork

@router.get("")
async def get_artworks(
    page: int = Query(1, ge=1), 
    limit: int = Query(12, ge=1, le=100), 
    year: int = Query(None), 
    sort: str = Query("newest")  # newest, oldest, views
):
    db = get_db()
    query = {}
    if year:
        query["year"] = year
    
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
    total = await db.arts.count_documents(query)
    cursor = db.arts.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
    
    items = []
    async for doc in cursor:
        artwork = serialize(dict(doc))
        artwork = await enrich_with_image(db, artwork)
        items.append(artwork)
    
    pages = ceil(total / limit) if total > 0 else 1
    return PaginatedResponse(items=items, total=total, page=page, pages=pages, has_next=page < pages, has_prev=page > 1)

@router.get("/years")
async def get_years():
    db = get_db()
    years = await db.arts.distinct("year")
    return sorted(years, reverse=True)

@router.get("/grouped")
async def get_grouped_artworks(limit_per_year: int = Query(7)):
    db = get_db()
    years = await db.arts.distinct("year")
    years = sorted(years, reverse=True)
    result = {}
    for year in years:
        cursor = db.arts.find({"year": year}).sort("created_at", -1).limit(limit_per_year)
        artworks = []
        async for doc in cursor:
            artwork = serialize(dict(doc))
            artwork = await enrich_with_image(db, artwork)
            artworks.append(artwork)
        result[str(year)] = artworks
    return result

@router.get("/by-slug/{slug}")
async def get_artwork_by_slug(slug: str):
    """Get artwork by slug"""
    db = get_db()
    artwork = await db.arts.find_one({"slug": slug})
    if not artwork:
        raise HTTPException(status_code=404, detail="Not found")
    
    artwork = serialize(dict(artwork))
    artwork = await enrich_with_image(db, artwork)
    return artwork

@router.get("/{artwork_id}")
async def get_artwork(artwork_id: str):
    db = get_db()
    
    # Try to find by ID first
    if ObjectId.is_valid(artwork_id):
        artwork = await db.arts.find_one({"_id": ObjectId(artwork_id)})
    else:
        # Try by slug
        artwork = await db.arts.find_one({"slug": artwork_id})
    
    if not artwork:
        raise HTTPException(status_code=404, detail="Not found")
    
    artwork = serialize(dict(artwork))
    artwork = await enrich_with_image(db, artwork)
    return artwork

@router.post("")
async def create_artwork(artwork: ArtWorkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    doc = artwork.model_dump()
    
    # Generate slug if not provided
    if not doc.get("slug"):
        doc["slug"] = generate_slug(doc["title"])
    
    # Ensure unique slug
    doc["slug"] = await ensure_unique_slug(db, doc["slug"])
    
    doc["created_at"] = datetime.utcnow()
    doc["views"] = 0
    result = await db.arts.insert_one(doc)
    created = await db.arts.find_one({"_id": result.inserted_id})
    created = serialize(dict(created))
    created = await enrich_with_image(db, created)
    return created

@router.put("/{artwork_id}")
async def update_artwork(artwork_id: str, artwork: ArtWorkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(artwork_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    data = artwork.model_dump()
    
    # Generate slug if not provided
    if not data.get("slug"):
        data["slug"] = generate_slug(data["title"])
    
    # Ensure unique slug (excluding current artwork)
    data["slug"] = await ensure_unique_slug(db, data["slug"], artwork_id)
    
    result = await db.arts.update_one({"_id": ObjectId(artwork_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = await db.arts.find_one({"_id": ObjectId(artwork_id)})
    updated = serialize(dict(updated))
    updated = await enrich_with_image(db, updated)
    return updated

@router.delete("/{artwork_id}")
async def delete_artwork(artwork_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(artwork_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.arts.delete_one({"_id": ObjectId(artwork_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}
