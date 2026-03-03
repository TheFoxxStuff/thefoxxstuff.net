from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import asyncio
import logging

from logging_config import setup_logging
setup_logging()

from database import connect_db, close_db, get_db
from cache import init_cache, close_cache, is_rate_limited, flush_view_buffers
from config import settings
from routers import music, blog, arts, links, auth, stats, upload, banner, views, profile, chat, presence

logger = logging.getLogger(__name__)


async def _view_flush_loop():
    """Фоновая задача: сбрасывает буфер просмотров из Redis → MongoDB каждые 30 сек."""
    while True:
        await asyncio.sleep(30)
        try:
            db = get_db()
            await flush_view_buffers(db)
        except Exception as exc:
            logger.warning("View flush loop error: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await init_cache()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    flush_task = asyncio.create_task(_view_flush_loop())
    logger.info("TheFoxxStuff API started")

    yield

    flush_task.cancel()
    try:
        await flush_task
    except asyncio.CancelledError:
        pass

    try:
        await flush_view_buffers(get_db())
    except Exception:
        pass

    await close_cache()
    await close_db()
    logger.info("TheFoxxStuff API stopped")


app = FastAPI(title="TheFoxxStuff API", version="1.0.0", lifespan=lifespan)

allowed_origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://front.thefoxxstuff.net",
    "https://front.thefoxxstuff.net",
    "https://api.thefoxxstuff.net",
    "http://thefoxxstuff.net",
    "https://thefoxxstuff.net",
    "https://www.thefoxxstuff.net",
    "https://dev.thefoxxstuff.net",
    "http://dev.thefoxxstuff.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers,
    )


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # WebSocket, статика и CORS preflight — без лимитов
    if request.url.path.startswith("/api/upload/file/"):
        return await call_next(request)
    if request.url.path.startswith("/api/presence/ws"):
        return await call_next(request)
    if request.method == "OPTIONS":  # CORS preflight не считаем
        return await call_next(request)

    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else "0.0.0.0")
    )

    # Увеличен лимит: 1000 запросов в минуту (было 300)
    if await is_rate_limited(client_ip, limit=1000, window=60):
        logger.warning("Rate limited: %s %s", client_ip, request.url.path)
        origin = request.headers.get("origin", "")
        headers = {}
        if origin in allowed_origins:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
            headers=headers,
        )

    return await call_next(request)


app.include_router(auth.router)
app.include_router(music.router)
app.include_router(blog.router)
app.include_router(arts.router)
app.include_router(links.router)
app.include_router(stats.router)
app.include_router(upload.router)
app.include_router(banner.router)
app.include_router(views.router)
app.include_router(profile.router)
app.include_router(chat.router)
app.include_router(presence.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_config=None,
    )
