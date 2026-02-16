from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_db, close_db
from config import settings
from routers import music, blog, arts, links, auth, stats, upload, banner, views, profile, chat
from pathlib import Path
import time
from collections import defaultdict

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    yield
    await close_db()

app = FastAPI(title="TheFoxxStuff API", version="1.0.0", lifespan=lifespan)

# CORS - allow frontend origin + localhost for dev
allowed_origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple rate limiting middleware
rate_limit_store = defaultdict(list)
RATE_LIMIT = 120  # requests per minute
RATE_WINDOW = 60  # seconds

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for static files
    if request.url.path.startswith("/api/upload/file/"):
        return await call_next(request)

    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "0.0.0.0").split(",")[0].strip()
    now = time.time()
    # Clean old entries
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if now - t < RATE_WINDOW]

    if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})

    rate_limit_store[client_ip].append(now)
    response = await call_next(request)
    return response

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
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
