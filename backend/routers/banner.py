import logging
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Response

from database import get_db
from models import BannerCreate
from auth import get_current_admin
from cache import cache_get_or_set, cache_delete
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/banner", tags=["banner"])

CACHE_KEY = "banner:current"


def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("")
async def get_banner(response: Response):
    response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_static}"

    async def fetch():
        db = get_db()
        banner = await db.banner.find_one()
        if not banner:
            default = {"slides": []}
            await db.banner.insert_one(default)
            banner = await db.banner.find_one()
        return serialize(dict(banner))

    return await cache_get_or_set(CACHE_KEY, fetch, settings.cache_ttl_static)


@router.put("")
async def update_banner(banner: BannerCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    existing = await db.banner.find_one()
    data = banner.model_dump()
    if existing:
        await db.banner.update_one({"_id": existing["_id"]}, {"$set": data})
    else:
        await db.banner.insert_one(data)
    await cache_delete(CACHE_KEY)
    return serialize(dict(await db.banner.find_one()))


@router.post("/slide")
async def add_slide(title: str, image: str, link: str = None, admin: dict = Depends(get_current_admin)):
    db = get_db()
    banner = await db.banner.find_one()
    if not banner:
        await db.banner.insert_one({"slides": []})
        banner = await db.banner.find_one()
    slides = banner.get("slides", [])
    slides.append({"id": str(ObjectId()), "title": title, "image": image, "link": link, "order": len(slides)})
    await db.banner.update_one({"_id": banner["_id"]}, {"$set": {"slides": slides}})
    await cache_delete(CACHE_KEY)
    return serialize(dict(await db.banner.find_one()))


@router.delete("/slide/{slide_id}")
async def remove_slide(slide_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    banner = await db.banner.find_one()
    if not banner:
        raise HTTPException(404, "Banner not found")
    slides = [s for s in banner.get("slides", []) if s.get("id") != slide_id]
    for i, slide in enumerate(slides):
        slide["order"] = i
    await db.banner.update_one({"_id": banner["_id"]}, {"$set": {"slides": slides}})
    await cache_delete(CACHE_KEY)
    return serialize(dict(await db.banner.find_one()))
