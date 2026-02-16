from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from database import get_db
from models import BannerCreate
from auth import get_current_admin

router = APIRouter(prefix="/api/banner", tags=["banner"])

def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("")
async def get_banner():
    """Get banner slides"""
    db = get_db()
    banner = await db.banner.find_one()
    if not banner:
        # Create default empty banner
        default = {"slides": []}
        await db.banner.insert_one(default)
        banner = await db.banner.find_one()
    return serialize(dict(banner))

@router.put("")
async def update_banner(banner: BannerCreate, admin: dict = Depends(get_current_admin)):
    """Update banner slides"""
    db = get_db()
    existing = await db.banner.find_one()
    
    data = banner.model_dump()
    
    if existing:
        await db.banner.update_one({"_id": existing["_id"]}, {"$set": data})
    else:
        await db.banner.insert_one(data)
    
    updated = await db.banner.find_one()
    return serialize(dict(updated))

@router.post("/slide")
async def add_slide(title: str, image: str, link: str = None, admin: dict = Depends(get_current_admin)):
    """Add a single slide to banner"""
    db = get_db()
    banner = await db.banner.find_one()
    
    if not banner:
        banner = {"slides": []}
        await db.banner.insert_one(banner)
        banner = await db.banner.find_one()
    
    slides = banner.get("slides", [])
    new_slide = {
        "id": str(ObjectId()),
        "title": title,
        "image": image,
        "link": link,
        "order": len(slides)
    }
    slides.append(new_slide)
    
    await db.banner.update_one({"_id": banner["_id"]}, {"$set": {"slides": slides}})
    updated = await db.banner.find_one()
    return serialize(dict(updated))

@router.delete("/slide/{slide_id}")
async def remove_slide(slide_id: str, admin: dict = Depends(get_current_admin)):
    """Remove a slide from banner"""
    db = get_db()
    banner = await db.banner.find_one()
    
    if not banner:
        raise HTTPException(404, "Banner not found")
    
    slides = [s for s in banner.get("slides", []) if s.get("id") != slide_id]
    
    # Reorder remaining slides
    for i, slide in enumerate(slides):
        slide["order"] = i
    
    await db.banner.update_one({"_id": banner["_id"]}, {"$set": {"slides": slides}})
    updated = await db.banner.find_one()
    return serialize(dict(updated))
