from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from database import get_db
from models import LinkCreate
from auth import get_current_admin

router = APIRouter(prefix="/api/links", tags=["links"])

def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("")
async def get_links():
    db = get_db()
    cursor = db.links.find().sort("order", 1)
    return [serialize(dict(doc)) async for doc in cursor]

@router.post("")
async def create_link(link: LinkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    doc = link.model_dump()
    result = await db.links.insert_one(doc)
    created = await db.links.find_one({"_id": result.inserted_id})
    return serialize(dict(created))

@router.put("/{link_id}")
async def update_link(link_id: str, link: LinkCreate, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.links.update_one({"_id": ObjectId(link_id)}, {"$set": link.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    updated = await db.links.find_one({"_id": ObjectId(link_id)})
    return serialize(dict(updated))

@router.delete("/{link_id}")
async def delete_link(link_id: str, admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.links.delete_one({"_id": ObjectId(link_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}
