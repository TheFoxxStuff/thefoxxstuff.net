import logging

from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_db():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.db = db.client[settings.database_name]
    await _ensure_indexes(db.db)

async def close_db():
    if db.client:
        db.client.close()

def get_db():
    return db.db


async def _ensure_indexes(database) -> None:
    """
    Индексы для запросов, которые раньше делали collection scan на каждый
    список/поиск/логин. Без них производительность деградирует линейно
    с ростом данных, а WiredTiger cache (ограничен 256MB) забивается сканами.
    create_index идемпотентен — безопасно вызывать при каждом старте.
    """
    try:
        await database.users.create_index("username", unique=True)
        await database.users.create_index("email", unique=True)

        await database.music.create_index("slug", unique=True, sparse=True)
        await database.music.create_index([("release_date", -1)])
        await database.music.create_index([("views", -1)])
        await database.music.create_index(
            [("title", "text"), ("genre", "text"), ("description", "text")],
            name="music_text_search",
            weights={"title": 10, "genre": 5, "description": 1},
        )

        await database.blog.create_index("slug", unique=True, sparse=True)
        await database.blog.create_index([("created_at", -1)])
        await database.blog.create_index([("views", -1)])
        await database.blog.create_index(
            [("title", "text"), ("content", "text"), ("excerpt", "text")],
            name="blog_text_search",
            weights={"title": 10, "excerpt": 5, "content": 1},
        )

        await database.arts.create_index("slug", unique=True, sparse=True)
        await database.arts.create_index([("year", -1), ("created_at", -1)])
        await database.arts.create_index([("views", -1)])
        await database.arts.create_index(
            [("title", "text"), ("description", "text")],
            name="arts_text_search",
            weights={"title": 10, "description": 1},
        )

        await database.chat_messages.create_index([("created_at", -1)])
        await database.images.create_index([("category", 1), ("created_at", -1)])
        await database.audio_files.create_index([("created_at", -1)])

        await database.view_records.create_index(
            [("entity_type", 1), ("entity_id", 1), ("date", 1)], unique=True
        )
        await database.daily_views.create_index(
            [("entity_type", 1), ("date", 1)], unique=True
        )

        logger.info("MongoDB indexes ensured")
    except Exception as exc:
        logger.warning("Failed to ensure MongoDB indexes: %s", exc)
