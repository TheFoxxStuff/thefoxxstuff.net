from fastapi import APIRouter, Depends, Query
from database import get_db
from auth import get_current_admin
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("")
async def get_stats(admin: dict = Depends(get_current_admin)):
    db = get_db()

    music_count = await db.music.count_documents({})
    blog_count = await db.blog.count_documents({})
    arts_count = await db.arts.count_documents({})
    users_count = await db.users.count_documents({})
    images_count = await db.images.count_documents({})

    # Use aggregation for efficient view counting instead of loading all documents
    music_views_result = await db.music.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$views"}}}
    ]).to_list(1)
    music_views = music_views_result[0]["total"] if music_views_result else 0

    blog_views_result = await db.blog.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$views"}}}
    ]).to_list(1)
    blog_views = blog_views_result[0]["total"] if blog_views_result else 0

    arts_views_result = await db.arts.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$views"}}}
    ]).to_list(1)
    arts_views = arts_views_result[0]["total"] if arts_views_result else 0

    return {
        "music": {"count": music_count, "views": music_views},
        "blog": {"count": blog_count, "views": blog_views},
        "arts": {"count": arts_count, "views": arts_views},
        "users": {"count": users_count},
        "images": {"count": images_count},
        "total_views": music_views + blog_views + arts_views
    }

@router.get("/views/chart")
async def get_views_chart(
    days: int = Query(30, ge=7, le=365),
    admin: dict = Depends(get_current_admin)
):
    """Get daily view counts for chart visualization"""
    db = get_db()
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get view records for the date range
    cursor = db.view_records.find({
        "date": {"$gte": start_date, "$lte": end_date}
    }).sort("date", 1)
    
    # Initialize data structure
    chart_data = []
    date_map = {}
    
    # Create entries for all days
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        date_map[date_str] = {
            "date": date_str,
            "music": 0,
            "blog": 0,
            "arts": 0,
            "total": 0
        }
        current += timedelta(days=1)
    
    # Fill in actual data
    async for record in cursor:
        date_str = record["date"].strftime("%Y-%m-%d")
        if date_str in date_map:
            entity_type = record.get("entity_type", "")
            count = record.get("count", 0)
            if entity_type in ["music", "blog", "arts"]:
                date_map[date_str][entity_type] += count
                date_map[date_str]["total"] += count
    
    # Convert to sorted list
    chart_data = [date_map[k] for k in sorted(date_map.keys())]
    
    return {
        "days": days,
        "data": chart_data,
        "summary": {
            "music": sum(d["music"] for d in chart_data),
            "blog": sum(d["blog"] for d in chart_data),
            "arts": sum(d["arts"] for d in chart_data),
            "total": sum(d["total"] for d in chart_data)
        }
    }

@router.post("/views/record")
async def record_view(
    entity_type: str,
    entity_id: str
):
    """Record a view for an entity (called internally)"""
    db = get_db()
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Update or create view record for today
    await db.view_records.update_one(
        {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "date": today
        },
        {
            "$inc": {"count": 1},
            "$setOnInsert": {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "date": today
            }
        },
        upsert=True
    )
    
    # Also record in aggregate daily stats
    await db.daily_views.update_one(
        {
            "entity_type": entity_type,
            "date": today
        },
        {
            "$inc": {"count": 1},
            "$setOnInsert": {
                "entity_type": entity_type,
                "date": today
            }
        },
        upsert=True
    )
    
    return {"recorded": True}

@router.get("/top")
async def get_top_content(
    limit: int = Query(5, ge=1, le=20),
    admin: dict = Depends(get_current_admin)
):
    """Get top viewed content"""
    db = get_db()
    
    # Top music
    top_music = []
    async for m in db.music.find().sort("views", -1).limit(limit):
        top_music.append({
            "_id": str(m["_id"]),
            "title": m.get("title", ""),
            "slug": m.get("slug", ""),
            "views": m.get("views", 0)
        })
    
    # Top blog posts
    top_blog = []
    async for b in db.blog.find().sort("views", -1).limit(limit):
        top_blog.append({
            "_id": str(b["_id"]),
            "title": b.get("title", ""),
            "slug": b.get("slug", ""),
            "views": b.get("views", 0)
        })
    
    # Top arts
    top_arts = []
    async for a in db.arts.find().sort("views", -1).limit(limit):
        top_arts.append({
            "_id": str(a["_id"]),
            "title": a.get("title", ""),
            "slug": a.get("slug", ""),
            "views": a.get("views", 0)
        })
    
    return {
        "music": top_music,
        "blog": top_blog,
        "arts": top_arts
    }

@router.get("/recent-views")
async def get_recent_views(
    days: int = Query(7, ge=1, le=30),
    admin: dict = Depends(get_current_admin)
):
    """Get views breakdown for recent days"""
    db = get_db()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"date": {"$gte": start_date}}},
        {"$group": {
            "_id": "$entity_type",
            "total": {"$sum": "$count"}
        }}
    ]
    
    results = {}
    async for doc in db.daily_views.aggregate(pipeline):
        results[doc["_id"]] = doc["total"]
    
    return {
        "period_days": days,
        "music": results.get("music", 0),
        "blog": results.get("blog", 0),
        "arts": results.get("arts", 0),
        "total": sum(results.values())
    }


@router.get("/search")
async def global_search(
    q: str = Query("", min_length=1, max_length=100),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Global search across music, blog, and arts with pagination.

    Раньше это был неанкорированный $regex по title/genre/description/content/excerpt
    без индекса — на каждый (публичный, без авторизации!) запрос три collection scan
    по всем трём коллекциям. С ростом контента это дешёвый способ положить Mongo.
    Теперь используются текстовые индексы (см. database.py) — MongoDB ищет по
    предпостроенному словарю токенов, а не сравнивает регэксп с каждым документом.
    """
    db = get_db()
    query = q.strip()
    if not query:
        return {"music": [], "blog": [], "arts": [], "total": {"music": 0, "blog": 0, "arts": 0}}

    text_query = {"$text": {"$search": query}}
    score = {"score": {"$meta": "textScore"}}
    skip = (page - 1) * limit

    music_total = await db.music.count_documents(text_query)
    blog_total = await db.blog.count_documents(text_query)
    arts_total = await db.arts.count_documents(text_query)

    music = []
    cursor = db.music.find(text_query, score).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)
    async for doc in cursor:
        music.append({
            "_id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "slug": doc.get("slug", ""),
            "genre": doc.get("genre", ""),
            "views": doc.get("views", 0),
            "type": "music"
        })

    blog = []
    cursor = db.blog.find(text_query, score).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)
    async for doc in cursor:
        excerpt = doc.get("excerpt", "")
        if len(excerpt) > 120:
            excerpt = excerpt[:117] + "..."
        blog.append({
            "_id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "slug": doc.get("slug", ""),
            "excerpt": excerpt,
            "views": doc.get("views", 0),
            "type": "blog"
        })

    arts = []
    cursor = db.arts.find(text_query, score).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)
    async for doc in cursor:
        arts.append({
            "_id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "slug": doc.get("slug", ""),
            "year": doc.get("year", ""),
            "views": doc.get("views", 0),
            "type": "arts"
        })

    return {
        "music": music,
        "blog": blog,
        "arts": arts,
        "total": {
            "music": music_total,
            "blog": blog_total,
            "arts": arts_total
        },
        "page": page,
        "limit": limit
    }
