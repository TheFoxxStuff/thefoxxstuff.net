from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from datetime import datetime
from database import get_db
from cache import get_redis
import time

router = APIRouter(prefix="/api/views", tags=["views"])


async def _publish_view_change(entity_type: str, entity_id: str):
    """Публикуем событие просмотра — presence WS сразу получит push с новым счётчиком."""
    redis = get_redis()
    if not redis:
        return
    try:
        import json as _json
        msg = _json.dumps({"change": "view", "entity_type": entity_type, "entity_id": entity_id, "ts": time.time()})
        await redis.publish("presence_changes", msg)
    except Exception:
        pass


@router.post("/record")
async def record_view(request: Request, entity_type: str, entity_id: str):
    """Record a view for an entity (called from the public site on page load)."""
    db = get_db()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    await db.view_records.update_one(
        {"entity_type": entity_type, "entity_id": entity_id, "date": today},
        {"$inc": {"count": 1}, "$setOnInsert": {"entity_type": entity_type, "entity_id": entity_id, "date": today}},
        upsert=True,
    )

    await db.daily_views.update_one(
        {"entity_type": entity_type, "date": today},
        {"$inc": {"count": 1}, "$setOnInsert": {"entity_type": entity_type, "date": today}},
        upsert=True,
    )

    collection_map = {"music": "music", "blog": "blog", "arts": "arts"}
    col_name = collection_map.get(entity_type)
    if col_name and ObjectId.is_valid(entity_id):
        await db[col_name].update_one({"_id": ObjectId(entity_id)}, {"$inc": {"views": 1}})

    await _publish_view_change(entity_type, entity_id)
    return {"recorded": True}
