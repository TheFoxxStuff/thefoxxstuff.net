import logging
from fastapi import APIRouter, Depends

from database import get_db
from models import AboutInfo
from auth import get_current_admin
from cache import cache_get, cache_set, cache_delete
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/about", tags=["about"])

CACHE_KEY = "about:current"


def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("")
async def get_about():
    cached = await cache_get(CACHE_KEY)
    if cached is not None:
        return cached

    db = get_db()
    about = await db.about.find_one()
    if not about:
        default = AboutInfo().model_dump()
        await db.about.insert_one(default)
        about = await db.about.find_one()
    result = serialize(dict(about))
    await cache_set(CACHE_KEY, result, settings.cache_ttl_static)
    return result


@router.put("")
async def update_about(about: AboutInfo, admin: dict = Depends(get_current_admin)):
    db = get_db()
    existing = await db.about.find_one()
    data = about.model_dump()
    if existing:
        await db.about.update_one({"_id": existing["_id"]}, {"$set": data})
    else:
        await db.about.insert_one(data)
    await cache_delete(CACHE_KEY)
    return serialize(dict(await db.about.find_one()))
