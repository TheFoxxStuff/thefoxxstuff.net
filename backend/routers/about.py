from fastapi import APIRouter, Depends
from database import get_db
from models import AboutInfo
from auth import get_current_admin

router = APIRouter(prefix="/api/about", tags=["about"])

def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("")
async def get_about():
    db = get_db()
    about = await db.about.find_one()
    if not about:
        default = AboutInfo().model_dump()
        await db.about.insert_one(default)
        about = await db.about.find_one()
    return serialize(dict(about))

@router.put("")
async def update_about(about: AboutInfo, admin: dict = Depends(get_current_admin)):
    db = get_db()
    existing = await db.about.find_one()
    data = about.model_dump()
    if existing:
        await db.about.update_one({"_id": existing["_id"]}, {"$set": data})
    else:
        await db.about.insert_one(data)
    updated = await db.about.find_one()
    return serialize(dict(updated))
