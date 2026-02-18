import logging
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Response

from database import get_db
from models import LinkCreate
from auth import get_current_admin
from cache import cache_get_or_set, cache_delete
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/links", tags=["links"])

CACHE_KEY = "links:all"


def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("")
async def get_links(response: Response):
    response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_static}"

    async def fetch():
        db = get_db()
        return [serialize(dict(doc)) async for doc in db.links.find().sort("order", 1)]

    return await cache_get_or_set(CACHE_KEY, fetch, settings.cache_ttl_static)


@router.post("")
async def create_link(link: LinkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    result = await db.links.insert_one(link.model_dump())
    created = serialize(dict(await db.links.find_one({"_id": result.inserted_id})))
    await cache_delete(CACHE_KEY)
    return created


@router.put("/{link_id}")
async def update_link(link_id: str, link: LinkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.links.update_one({"_id": ObjectId(link_id)}, {"$set": link.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = serialize(dict(await db.links.find_one({"_id": ObjectId(link_id)})))
    await cache_delete(CACHE_KEY)
    return updated


@router.delete("/{link_id}")
async def delete_link(link_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.links.delete_one({"_id": ObjectId(link_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    await cache_delete(CACHE_KEY)
    return {"deleted": True}
