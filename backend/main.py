from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path

from logging_config import setup_logging
setup_logging()  # must be first

import logging
from database import connect_db, close_db
from cache import init_cache, close_cache, is_rate_limited
from config import settings
from routers import music, blog, arts, links, auth, stats, upload, banner, views, profile, chat

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await init_cache()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    logger.info("TheFoxxStuff API started")
    yield
    await close_cache()
    await close_db()
    logger.info("TheFoxxStuff API stopped")


app = FastAPI(title="TheFoxxStuff API", version="1.0.0", lifespan=lifespan)

# CORS
allowed_origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://front.thefoxxstuff.net",
    "https://front.thefoxxstuff.net",
    "https://api.thefoxxstuff.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting via Redis (falls back to allow when Redis is down)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/upload/file/"):
        return await call_next(request)

    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else "0.0.0.0")
    )

    if await is_rate_limited(client_ip, limit=120, window=60):
        logger.warning("Rate limit hit: %s %s", client_ip, request.url.path)
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})

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
        log_config=None,  # use our logging_config
    )
