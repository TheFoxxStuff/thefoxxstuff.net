from fastapi import APIRouter, HTTPException, Request, Depends, Query
from bson import ObjectId
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_admin
import json
import struct
import socket

router = APIRouter(prefix="/api/views", tags=["views"])


def ip_to_int(ip: str) -> int:
    """Convert IP string to integer for compact storage"""
    try:
        return struct.unpack("!I", socket.inet_aton(ip))[0]
    except:
        return 0


def get_client_ip(request: Request) -> str:
    """Extract real client IP from request headers"""
    # Check X-Forwarded-For first (reverse proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # Check X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    # Fallback to client host
    return request.client.host if request.client else "0.0.0.0"


async def geolocate_ip(ip: str) -> dict:
    """
    Geolocate IP using ip-api.com (free, no key needed, 45 req/min).
    Returns {country, city, lat, lon, countryCode} or empty dict.
    """
    import httpx
    if ip in ("127.0.0.1", "0.0.0.0", "::1", "localhost"):
        return {"country": "Local", "city": "localhost", "lat": 0, "lon": 0, "countryCode": "XX"}
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=country,city,lat,lon,countryCode")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("country"):
                    return data
    except:
        pass
    return {}


@router.post("/record")
async def record_view_with_ip(request: Request, entity_type: str, entity_id: str):
    """Record a view with IP + geolocation tracking"""
    db = get_db()
    ip = get_client_ip(request)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.utcnow()

    # Check if this IP already viewed this entity today (deduplicate)
    existing = await db.ip_views.find_one({
        "ip": ip,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "date": today
    })

    if existing:
        # Already viewed today from this IP - just increment hit count
        await db.ip_views.update_one({"_id": existing["_id"]}, {"$inc": {"hits": 1}})
        return {"recorded": True, "unique": False}

    # Geolocate
    geo = await geolocate_ip(ip)

    # Record unique IP view
    await db.ip_views.insert_one({
        "ip": ip,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "date": today,
        "timestamp": now,
        "hits": 1,
        "country": geo.get("country", "Unknown"),
        "city": geo.get("city", "Unknown"),
        "country_code": geo.get("countryCode", "XX"),
        "lat": geo.get("lat", 0),
        "lon": geo.get("lon", 0),
        "location": f"{geo.get('country', 'Unknown')}, {geo.get('city', 'Unknown')}"
    })

    # Update view_records (daily aggregate - existing system)
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

    # Increment entity views count
    collection_map = {"music": "music", "blog": "blog", "arts": "arts"}
    col_name = collection_map.get(entity_type)
    if col_name and ObjectId.is_valid(entity_id):
        await db[col_name].update_one({"_id": ObjectId(entity_id)}, {"$inc": {"views": 1}})

    return {"recorded": True, "unique": True}


@router.get("/map")
async def get_views_map(
    days: int = Query(30, ge=1, le=365),
    admin: dict = Depends(get_current_admin)
):
    """Get aggregated view locations for map display"""
    db = get_db()
    start_date = datetime.utcnow() - timedelta(days=days)

    # Aggregate views by country+city with coordinates
    pipeline = [
        {"$match": {"date": {"$gte": start_date}, "lat": {"$ne": 0}}},
        {"$group": {
            "_id": {"country": "$country", "city": "$city", "country_code": "$country_code"},
            "count": {"$sum": 1},
            "lat": {"$first": "$lat"},
            "lon": {"$first": "$lon"},
            "last_view": {"$max": "$timestamp"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 500}
    ]

    locations = []
    async for doc in db.ip_views.aggregate(pipeline):
        locations.append({
            "country": doc["_id"]["country"],
            "city": doc["_id"]["city"],
            "country_code": doc["_id"]["country_code"],
            "count": doc["count"],
            "lat": doc["lat"],
            "lon": doc["lon"],
            "last_view": doc["last_view"].isoformat() if doc.get("last_view") else None
        })

    # Country summary
    country_pipeline = [
        {"$match": {"date": {"$gte": start_date}}},
        {"$group": {
            "_id": {"country": "$country", "country_code": "$country_code"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]

    countries = []
    async for doc in db.ip_views.aggregate(country_pipeline):
        countries.append({
            "country": doc["_id"]["country"],
            "country_code": doc["_id"]["country_code"],
            "count": doc["count"]
        })

    # Total unique IPs
    total_unique = await db.ip_views.count_documents({"date": {"$gte": start_date}})

    return {
        "locations": locations,
        "countries": countries,
        "total_unique_views": total_unique,
        "days": days
    }


@router.get("/recent")
async def get_recent_views_list(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(get_current_admin)
):
    """Get recent individual view records"""
    db = get_db()
    skip = (page - 1) * limit

    total = await db.ip_views.count_documents({})
    cursor = db.ip_views.find().sort("timestamp", -1).skip(skip).limit(limit)

    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }
