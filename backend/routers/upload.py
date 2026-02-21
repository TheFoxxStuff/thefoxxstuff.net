from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse
from bson import ObjectId
from datetime import datetime
from pathlib import Path
from PIL import Image
import os
import uuid
import re
import asyncio
import subprocess
import aiofiles
from database import get_db
from config import settings
from auth import get_current_admin

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Ensure upload directories exist
UPLOAD_DIR = Path(settings.upload_dir)

# Organized directory structure
CATEGORIES = ["music", "blog", "arts", "markdown", "banner"]
VARIANTS = ["original", "thumb", "medium"]

def ensure_directories():
    """Create all necessary directories"""
    for category in CATEGORIES:
        for variant in VARIANTS:
            (UPLOAD_DIR / category / variant).mkdir(parents=True, exist_ok=True)
    # Also create gallery subdirectory for music
    for variant in VARIANTS:
        (UPLOAD_DIR / "music" / "gallery" / variant).mkdir(parents=True, exist_ok=True)
    # Audio directories
    (UPLOAD_DIR / "music" / "audio" / "original").mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "music" / "audio" / "mp3_320").mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "music" / "audio" / "mp3_128").mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "music" / "audio" / "opus").mkdir(parents=True, exist_ok=True)

ensure_directories()

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace spaces with underscores
    text = text.lower().strip()
    # Remove non-alphanumeric characters except underscores and hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace whitespace with underscores
    text = re.sub(r'[\s]+', '_', text)
    # Remove duplicate underscores
    text = re.sub(r'_+', '_', text)
    return text

def get_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

def generate_filename(base_name: str, ext: str) -> str:
    """Generate filename from base name"""
    slug = slugify(base_name)
    if not slug:
        slug = uuid.uuid4().hex[:8]
    return f"{slug}.{ext}"

def create_thumbnail(input_path: Path, output_path: Path, size: tuple, format: str = 'WEBP') -> tuple:
    """Create resized version maintaining aspect ratio in WebP format"""
    with Image.open(input_path) as img:
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (18, 18, 18))  # dark-900 color
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save as WebP for medium and thumb
        if format == 'WEBP':
            img.save(output_path, 'WEBP', quality=85, method=6)
        else:
            img.save(output_path, format, quality=85, optimize=True)
        
        return img.size

async def process_image(
    file: UploadFile, 
    category: str = "markdown",
    custom_name: str = None,
    parent_id: str = None,
    is_gallery: bool = False
) -> dict:
    """Process uploaded image and create thumbnails"""
    ext = get_extension(file.filename)
    if ext not in settings.allowed_extensions:
        raise HTTPException(400, f"File type not allowed. Allowed: {', '.join(settings.allowed_extensions)}")
    
    # Generate base filename from custom name or original filename
    base_name = custom_name or file.filename.rsplit('.', 1)[0]
    base_slug = slugify(base_name)
    
    # Add unique suffix to prevent collisions
    unique_suffix = uuid.uuid4().hex[:6]
    filename_base = f"{base_slug}_{unique_suffix}"
    
    # Determine paths based on category and gallery flag
    if category == "music" and is_gallery:
        base_dir = UPLOAD_DIR / "music" / "gallery"
    else:
        base_dir = UPLOAD_DIR / category
    
    original_filename = f"{filename_base}_original.{ext}"
    thumb_filename = f"{filename_base}_thumb.webp"
    medium_filename = f"{filename_base}_medium.webp"
    
    original_path = base_dir / "original" / original_filename
    thumb_path = base_dir / "thumb" / thumb_filename
    medium_path = base_dir / "medium" / medium_filename
    
    # Read and save original
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(400, f"File too large. Max size: {settings.max_file_size // (1024*1024)}MB")
    
    async with aiofiles.open(original_path, 'wb') as f:
        await f.write(content)
    
    # Get original dimensions
    with Image.open(original_path) as img:
        width, height = img.size
    
    # Create thumbnails in WebP format
    thumb_size = create_thumbnail(original_path, thumb_path, settings.thumb_size, 'WEBP')
    medium_size = create_thumbnail(original_path, medium_path, settings.medium_size, 'WEBP')
    
    # Build relative paths for storage
    if category == "music" and is_gallery:
        rel_base = f"music/gallery"
    else:
        rel_base = category
    
    return {
        "filename": original_filename,
        "original": f"{rel_base}/original/{original_filename}",
        "thumb": f"{rel_base}/thumb/{thumb_filename}",
        "medium": f"{rel_base}/medium/{medium_filename}",
        "size": len(content),
        "width": width,
        "height": height,
        "original_filename": file.filename,
        "category": category,
        "parent_id": parent_id,
        "custom_name": custom_name,
        "is_gallery": is_gallery
    }

@router.post("")
async def upload_image(
    file: UploadFile = File(...), 
    category: str = Query("markdown", description="Category: music, blog, arts, markdown, banner"),
    custom_name: str = Query(None, description="Custom name for the file"),
    parent_id: str = Query(None, description="Parent entity ID"),
    is_gallery: bool = Query(False, description="Is this a gallery image for music"),
    admin: dict = Depends(get_current_admin)
):
    """Upload a single image"""
    db = get_db()
    
    if category not in CATEGORIES:
        category = "markdown"
    
    try:
        result = await process_image(file, category, custom_name, parent_id, is_gallery)
    except Exception as e:
        raise HTTPException(400, str(e))
    
    doc = {
        **result,
        "created_at": datetime.utcnow()
    }
    inserted = await db.images.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    
    return doc

@router.post("/multiple")
async def upload_multiple_images(
    files: list[UploadFile] = File(...), 
    category: str = Query("markdown"),
    parent_id: str = Query(None),
    is_gallery: bool = Query(False),
    admin: dict = Depends(get_current_admin)
):
    """Upload multiple images"""
    db = get_db()
    results = []
    
    if category not in CATEGORIES:
        category = "markdown"
    
    for file in files:
        try:
            result = await process_image(file, category, None, parent_id, is_gallery)
            doc = {
                **result,
                "created_at": datetime.utcnow()
            }
            inserted = await db.images.insert_one(doc)
            doc["_id"] = str(inserted.inserted_id)
            results.append(doc)
        except Exception as e:
            results.append({"error": str(e), "filename": file.filename})
    
    return results

@router.get("/{image_id}")
async def get_image_info(image_id: str):
    """Get image metadata"""
    db = get_db()
    if not ObjectId.is_valid(image_id):
        raise HTTPException(400, "Invalid image ID")
    
    image = await db.images.find_one({"_id": ObjectId(image_id)})
    if not image:
        raise HTTPException(404, "Image not found")
    
    image["_id"] = str(image["_id"])
    return image

@router.get("/file/{path:path}")
async def serve_image(path: str):
    """Serve image file with organized paths"""
    # Sanitize path to prevent directory traversal
    safe_path = Path(path).as_posix()
    if '..' in safe_path:
        raise HTTPException(400, "Invalid path")
    
    file_path = UPLOAD_DIR / safe_path
    if not file_path.exists():
        # Try legacy path structure for backward compatibility
        parts = safe_path.split('/')
        if len(parts) == 2:  # old format: variant/filename
            variant, filename = parts
            # Check each category
            for cat in CATEGORIES:
                legacy_path = UPLOAD_DIR / cat / variant / filename
                if legacy_path.exists():
                    file_path = legacy_path
                    break
            # Also check root level (very old format)
            if not file_path.exists():
                file_path = UPLOAD_DIR / variant / filename
    
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(file_path)

@router.delete("/{image_id}")
async def delete_image(image_id: str, admin: dict = Depends(get_current_admin)):
    """Delete an image and its thumbnails"""
    db = get_db()
    if not ObjectId.is_valid(image_id):
        raise HTTPException(400, "Invalid image ID")
    
    image = await db.images.find_one({"_id": ObjectId(image_id)})
    if not image:
        raise HTTPException(404, "Image not found")
    
    # Delete files
    for path_key in ["original", "thumb", "medium"]:
        path_value = image.get(path_key, "")
        if path_value:
            file_path = UPLOAD_DIR / path_value
            if file_path.exists():
                file_path.unlink()
    
    await db.images.delete_one({"_id": ObjectId(image_id)})
    return {"deleted": True}

# Markdown image upload endpoint
@router.post("/markdown")
async def upload_markdown_image(file: UploadFile = File(...), admin: dict = Depends(get_current_admin)):
    """Upload image for markdown content, returns URL for embedding"""
    db = get_db()
    
    try:
        result = await process_image(file, "markdown")
    except Exception as e:
        raise HTTPException(400, str(e))
    
    doc = {
        **result,
        "created_at": datetime.utcnow()
    }
    inserted = await db.images.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    
    return {
        "id": doc["_id"],
        "url": f"/api/upload/file/{doc['medium']}",
        "thumb_url": f"/api/upload/file/{doc['thumb']}",
        "original_url": f"/api/upload/file/{doc['original']}",
        "markdown": f"![{result['original_filename']}](/api/upload/file/{doc['medium']})"
    }

# Cleanup unused images
@router.post("/cleanup")
async def cleanup_unused_images(admin: dict = Depends(get_current_admin)):
    """Find and delete images that are not referenced by any entity"""
    db = get_db()
    
    # Collect all used image IDs
    used_ids = set()
    
    # From music (cover_image and gallery)
    async for music in db.music.find({}, {"cover_image": 1, "gallery": 1}):
        if music.get("cover_image"):
            used_ids.add(music["cover_image"])
        for g in music.get("gallery", []):
            if isinstance(g, dict) and g.get("image_id"):
                used_ids.add(g["image_id"])
            elif isinstance(g, str):
                used_ids.add(g)
    
    # From blog (cover_image)
    async for blog in db.blog.find({}, {"cover_image": 1}):
        if blog.get("cover_image"):
            used_ids.add(blog["cover_image"])
    
    # From arts (image, og_image)
    async for art in db.arts.find({}, {"image": 1, "og_image": 1}):
        if art.get("image"):
            used_ids.add(art["image"])
        if art.get("og_image"):
            used_ids.add(art["og_image"])
    
    # From banner
    banner = await db.banner.find_one()
    if banner:
        for slide in banner.get("slides", []):
            if slide.get("image"):
                used_ids.add(slide["image"])
    
    # From about
    about = await db.about.find_one()
    if about and about.get("image"):
        used_ids.add(about["image"])
    
    # Find unused images
    used_object_ids = [ObjectId(id) for id in used_ids if ObjectId.is_valid(id)]
    
    unused_cursor = db.images.find({"_id": {"$nin": used_object_ids}})
    deleted_count = 0
    errors = []
    
    async for image in unused_cursor:
        try:
            # Delete files
            for path_key in ["original", "thumb", "medium"]:
                path_value = image.get(path_key, "")
                if path_value:
                    file_path = UPLOAD_DIR / path_value
                    if file_path.exists():
                        file_path.unlink()
            
            await db.images.delete_one({"_id": image["_id"]})
            deleted_count += 1
        except Exception as e:
            errors.append({"id": str(image["_id"]), "error": str(e)})
    
    return {
        "deleted_count": deleted_count,
        "errors": errors,
        "total_used": len(used_ids)
    }

# Get all images with filtering
@router.get("")
async def list_images(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    unused_only: bool = Query(False),
    admin: dict = Depends(get_current_admin)
):
    """List all images with pagination and filtering"""
    db = get_db()
    
    query = {}
    if category:
        query["category"] = category
    
    if unused_only:
        # Get all used IDs first
        used_ids = set()
        
        async for music in db.music.find({}, {"cover_image": 1, "gallery": 1}):
            if music.get("cover_image"):
                used_ids.add(music["cover_image"])
            for g in music.get("gallery", []):
                if isinstance(g, dict) and g.get("image_id"):
                    used_ids.add(g["image_id"])
                elif isinstance(g, str):
                    used_ids.add(g)
        
        async for blog in db.blog.find({}, {"cover_image": 1}):
            if blog.get("cover_image"):
                used_ids.add(blog["cover_image"])
        
        async for art in db.arts.find({}, {"image": 1}):
            if art.get("image"):
                used_ids.add(art["image"])
        
        used_object_ids = [ObjectId(id) for id in used_ids if ObjectId.is_valid(id)]
        query["_id"] = {"$nin": used_object_ids}
    
    from math import ceil
    skip = (page - 1) * limit
    total = await db.images.count_documents(query)
    cursor = db.images.find(query).sort("created_at", -1).skip(skip).limit(limit)
    
    items = []
    async for img in cursor:
        img["_id"] = str(img["_id"])
        items.append(img)
    
    pages = ceil(total / limit) if total > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1
    }


# ─── Audio Upload & Conversion ───────────────────────────────────────────────

ALLOWED_AUDIO_EXT = {"flac", "mp3"}

def audio_slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '_', text)
    text = re.sub(r'_+', '_', text)
    return text

def _run_ffmpeg(cmd):
    """Run ffmpeg/ffprobe synchronously (called from thread)"""
    return subprocess.run(cmd, capture_output=True, text=True)


async def convert_audio(input_path: Path, output_path: Path, codec: str, bitrate: str):
    """Convert audio using ffmpeg (Windows-compatible via asyncio.to_thread)"""
    cmd = ["ffmpeg", "-y", "-i", str(input_path)]
    if codec == "libmp3lame":
        cmd += ["-codec:a", "libmp3lame", "-b:a", bitrate, "-q:a", "0"]
    elif codec == "libopus":
        cmd += ["-codec:a", "libopus", "-b:a", bitrate, "-vbr", "on"]
    cmd.append(str(output_path))
    
    result = await asyncio.to_thread(_run_ffmpeg, cmd)
    if result.returncode != 0:
        raise Exception(f"ffmpeg error: {result.stderr}")


async def get_audio_duration(file_path: Path) -> str:
    """Get audio duration using ffprobe, returns MM:SS (Windows-compatible)"""
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
    ]
    result = await asyncio.to_thread(_run_ffmpeg, cmd)
    if result.returncode != 0:
        return "00:00"
    try:
        seconds = float(result.stdout.strip())
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    except:
        return "00:00"


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    custom_name: str = Query(None, description="Custom name for the file"),
    generate_mp3_128: bool = Query(False, description="Also generate MP3 128kbps"),
    admin: dict = Depends(get_current_admin)
):
    """Upload audio file (FLAC or MP3) and convert to MP3 320, Opus 128, optionally MP3 128"""
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_AUDIO_EXT:
        raise HTTPException(400, f"Audio type not allowed. Allowed: {', '.join(ALLOWED_AUDIO_EXT)}")
    
    base_name = custom_name or file.filename.rsplit('.', 1)[0]
    base_slug = audio_slugify(base_name)
    unique_suffix = uuid.uuid4().hex[:6]
    filename_base = f"{base_slug}_{unique_suffix}"
    
    audio_dir = UPLOAD_DIR / "music" / "audio"
    
    # Save original
    original_filename = f"{filename_base}.{ext}"
    original_path = audio_dir / "original" / original_filename
    
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:  # 100MB limit for audio
        raise HTTPException(400, "Audio file too large. Max 100MB.")
    
    async with aiofiles.open(original_path, 'wb') as f:
        await f.write(content)
    
    # Get duration
    duration = await get_audio_duration(original_path)
    
    result = {
        "original_path": f"music/audio/original/{original_filename}",
        "original_filename": file.filename,
        "duration": duration,
        "size": len(content),
    }
    
    # Convert to MP3 320kbps
    mp3_320_filename = f"{filename_base}.mp3"
    mp3_320_path = audio_dir / "mp3_320" / mp3_320_filename
    try:
        await convert_audio(original_path, mp3_320_path, "libmp3lame", "320k")
        result["mp3_320_path"] = f"music/audio/mp3_320/{mp3_320_filename}"
    except Exception as e:
        result["mp3_320_error"] = str(e)
    
    # Convert to Opus 128kbps
    opus_filename = f"{filename_base}.opus"
    opus_path = audio_dir / "opus" / opus_filename
    try:
        await convert_audio(original_path, opus_path, "libopus", "128k")
        result["opus_path"] = f"music/audio/opus/{opus_filename}"
    except Exception as e:
        result["opus_error"] = str(e)
    
    # Optionally convert to MP3 128kbps
    if generate_mp3_128:
        mp3_128_filename = f"{filename_base}.mp3"
        mp3_128_path = audio_dir / "mp3_128" / mp3_128_filename
        try:
            await convert_audio(original_path, mp3_128_path, "libmp3lame", "128k")
            result["mp3_128_path"] = f"music/audio/mp3_128/{mp3_128_filename}"
        except Exception as e:
            result["mp3_128_error"] = str(e)
    
    # Save to DB
    db = get_db()
    doc = {
        **result,
        "type": "audio",
        "custom_name": custom_name,
        "created_at": datetime.utcnow()
    }
    inserted = await db.audio_files.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    
    return doc


@router.put("/audio/{audio_id}/toggle-mp3-128")
async def toggle_mp3_128(audio_id: str, enable: bool = Query(...), admin: dict = Depends(get_current_admin)):
    """Enable or disable MP3 128kbps for an audio file"""
    db = get_db()
    if not ObjectId.is_valid(audio_id):
        raise HTTPException(400, "Invalid audio ID")
    
    audio = await db.audio_files.find_one({"_id": ObjectId(audio_id)})
    if not audio:
        raise HTTPException(404, "Audio not found")
    
    if enable and not audio.get("mp3_128_path"):
        # Generate MP3 128kbps from original
        original_path = UPLOAD_DIR / audio["original_path"]
        if not original_path.exists():
            raise HTTPException(400, "Original audio file not found")
        
        filename_base = original_path.stem
        mp3_128_filename = f"{filename_base}.mp3"
        mp3_128_path = UPLOAD_DIR / "music" / "audio" / "mp3_128" / mp3_128_filename
        
        try:
            await convert_audio(original_path, mp3_128_path, "libmp3lame", "128k")
            await db.audio_files.update_one(
                {"_id": ObjectId(audio_id)},
                {"$set": {"mp3_128_path": f"music/audio/mp3_128/{mp3_128_filename}"}}
            )
        except Exception as e:
            raise HTTPException(500, f"Conversion failed: {str(e)}")
    
    elif not enable and audio.get("mp3_128_path"):
        # Delete MP3 128kbps file
        mp3_128_file = UPLOAD_DIR / audio["mp3_128_path"]
        if mp3_128_file.exists():
            mp3_128_file.unlink()
        await db.audio_files.update_one(
            {"_id": ObjectId(audio_id)},
            {"$unset": {"mp3_128_path": ""}}
        )
    
    updated = await db.audio_files.find_one({"_id": ObjectId(audio_id)})
    updated["_id"] = str(updated["_id"])
    return updated


@router.get("/audio/{audio_id}")
async def get_audio_info(audio_id: str):
    """Get audio file metadata"""
    db = get_db()
    if not ObjectId.is_valid(audio_id):
        raise HTTPException(400, "Invalid audio ID")
    audio = await db.audio_files.find_one({"_id": ObjectId(audio_id)})
    if not audio:
        raise HTTPException(404, "Audio not found")
    audio["_id"] = str(audio["_id"])
    return audio


@router.delete("/audio/{audio_id}")
async def delete_audio(audio_id: str, admin: dict = Depends(get_current_admin)):
    """Delete an audio file and all its conversions"""
    db = get_db()
    if not ObjectId.is_valid(audio_id):
        raise HTTPException(400, "Invalid audio ID")
    
    audio = await db.audio_files.find_one({"_id": ObjectId(audio_id)})
    if not audio:
        raise HTTPException(404, "Audio not found")
    
    # Delete all files
    for key in ["original_path", "mp3_320_path", "mp3_128_path", "opus_path"]:
        path_val = audio.get(key)
        if path_val:
            file_path = UPLOAD_DIR / path_val
            if file_path.exists():
                file_path.unlink()
    
    await db.audio_files.delete_one({"_id": ObjectId(audio_id)})
    return {"deleted": True}


@router.get("/audio/file/{path:path}")
async def serve_audio_file(path: str):
    """Serve audio file"""
    safe_path = Path(path).as_posix()
    if '..' in safe_path:
        raise HTTPException(400, "Invalid path")
    
    file_path = UPLOAD_DIR / safe_path
    if not file_path.exists():
        raise HTTPException(404, "Audio file not found")
    
    # Determine media type
    ext = file_path.suffix.lower()
    media_types = {
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.opus': 'audio/opus',
        '.ogg': 'audio/ogg',
    }
    media_type = media_types.get(ext, 'application/octet-stream')
    
    return FileResponse(file_path, media_type=media_type)


@router.post("/audio/write-metadata")
async def write_audio_metadata(
    request_body: dict,
    admin: dict = Depends(get_current_admin)
):
    """
    Write ID3/Vorbis metadata to all audio variants of a track.
    Expects JSON with:
      - track_paths: dict with keys original_path, mp3_320_path, mp3_128_path (optional)
      - title: track title
      - artist: artist name
      - album_artist: album artist
      - album: album name
      - year: year string
      - track_number: track number (int)
      - genre: genre string
      - comment: production notes / comment
      - cover_image_id: image ID for cover art (optional)
      - publisher: publisher name
      - copyright: copyright string
      - url: artist URL
    """
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TDRC, TRCK, TCON, COMM, TPUB, TCOP, WOAR, APIC
    from mutagen.flac import FLAC
    from mutagen.oggopus import OggOpus
    from mutagen import File as MutagenFile
    import io

    data = request_body
    results = {}

    # Load cover art if provided
    cover_data = None
    cover_mime = "image/jpeg"
    if data.get("cover_image_id"):
        db = get_db()
        if ObjectId.is_valid(data["cover_image_id"]):
            img_doc = await db.images.find_one({"_id": ObjectId(data["cover_image_id"])})
            if img_doc:
                # Use medium variant for metadata (not too large)
                cover_path = UPLOAD_DIR / (img_doc.get("medium") or img_doc.get("original", ""))
                if cover_path.exists():
                    async with aiofiles.open(cover_path, "rb") as f:
                        cover_data = await f.read()
                    ext = cover_path.suffix.lower()
                    if ext == ".webp":
                        # Convert webp to jpeg for max compatibility
                        from PIL import Image as PILImage
                        img = PILImage.open(io.BytesIO(cover_data))
                        buf = io.BytesIO()
                        img.convert("RGB").save(buf, "JPEG", quality=90)
                        cover_data = buf.getvalue()
                        cover_mime = "image/jpeg"
                    elif ext == ".png":
                        cover_mime = "image/png"
                    else:
                        cover_mime = "image/jpeg"

    def _write_mp3_tags(fpath):
        """Write ID3 tags to MP3 file"""
        try:
            audio = MP3(str(fpath))
            if audio.tags is None:
                audio.add_tags()
            tags = audio.tags

            if data.get("title"):
                tags.add(TIT2(encoding=3, text=data["title"]))
            if data.get("artist"):
                tags.add(TPE1(encoding=3, text=data["artist"]))
            if data.get("album_artist"):
                tags.add(TPE2(encoding=3, text=data["album_artist"]))
            if data.get("album"):
                tags.add(TALB(encoding=3, text=data["album"]))
            if data.get("year"):
                tags.add(TDRC(encoding=3, text=str(data["year"])))
            if data.get("track_number"):
                tags.add(TRCK(encoding=3, text=str(data["track_number"])))
            if data.get("genre"):
                tags.add(TCON(encoding=3, text=data["genre"]))
            if data.get("comment"):
                tags.add(COMM(encoding=3, lang="eng", desc="", text=data["comment"]))
            if data.get("publisher"):
                tags.add(TPUB(encoding=3, text=data["publisher"]))
            if data.get("copyright"):
                tags.add(TCOP(encoding=3, text=data["copyright"]))
            if data.get("url"):
                tags.add(WOAR(url=data["url"]))
            if cover_data:
                tags.add(APIC(
                    encoding=3,
                    mime=cover_mime,
                    type=3,  # Cover (front)
                    desc="Cover",
                    data=cover_data
                ))

            audio.save()
            return True
        except Exception as e:
            return str(e)

    def _write_flac_tags(fpath):
        """Write Vorbis tags to FLAC file"""
        try:
            audio = FLAC(str(fpath))
            if data.get("title"):
                audio["title"] = data["title"]
            if data.get("artist"):
                audio["artist"] = data["artist"]
            if data.get("album_artist"):
                audio["albumartist"] = data["album_artist"]
            if data.get("album"):
                audio["album"] = data["album"]
            if data.get("year"):
                audio["date"] = str(data["year"])
            if data.get("track_number"):
                audio["tracknumber"] = str(data["track_number"])
            if data.get("genre"):
                audio["genre"] = data["genre"]
            if data.get("comment"):
                audio["comment"] = data["comment"]
            if data.get("publisher"):
                audio["organization"] = data["publisher"]
            if data.get("copyright"):
                audio["copyright"] = data["copyright"]

            if cover_data:
                from mutagen.flac import Picture
                pic = Picture()
                pic.type = 3
                pic.mime = cover_mime
                pic.desc = "Cover"
                pic.data = cover_data
                audio.clear_pictures()
                audio.add_picture(pic)

            audio.save()
            return True
        except Exception as e:
            return str(e)

    def _write_opus_tags(fpath):
        """Write tags to Opus file"""
        try:
            audio = OggOpus(str(fpath))
            if data.get("title"):
                audio["title"] = data["title"]
            if data.get("artist"):
                audio["artist"] = data["artist"]
            if data.get("album_artist"):
                audio["albumartist"] = data["album_artist"]
            if data.get("album"):
                audio["album"] = data["album"]
            if data.get("year"):
                audio["date"] = str(data["year"])
            if data.get("track_number"):
                audio["tracknumber"] = str(data["track_number"])
            if data.get("genre"):
                audio["genre"] = data["genre"]
            if data.get("comment"):
                audio["comment"] = data["comment"]
            if data.get("publisher"):
                audio["organization"] = data["publisher"]
            if data.get("copyright"):
                audio["copyright"] = data["copyright"]

            # Opus embeds cover via METADATA_BLOCK_PICTURE (base64 encoded FLAC picture)
            if cover_data:
                import base64
                from mutagen.flac import Picture
                pic = Picture()
                pic.type = 3
                pic.mime = cover_mime
                pic.desc = "Cover"
                pic.data = cover_data
                audio["metadata_block_picture"] = base64.b64encode(pic.write()).decode("ascii")

            audio.save()
            return True
        except Exception as e:
            return str(e)

    # Process each provided path
    paths = data.get("track_paths", {})

    for key, path_val in paths.items():
        if not path_val:
            continue
        fpath = UPLOAD_DIR / path_val
        if not fpath.exists():
            results[key] = f"File not found: {path_val}"
            continue

        ext = fpath.suffix.lower()
        if ext == ".mp3":
            res = await asyncio.to_thread(_write_mp3_tags, fpath)
        elif ext == ".flac":
            res = await asyncio.to_thread(_write_flac_tags, fpath)
        elif ext in (".opus", ".ogg"):
            res = await asyncio.to_thread(_write_opus_tags, fpath)
        else:
            res = f"Unsupported format: {ext}"
        results[key] = "ok" if res is True else res

    return {"results": results}


@router.get("/audio/list")
async def list_audio_files(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    admin: dict = Depends(get_current_admin)
):
    """List all audio files with pagination"""
    from math import ceil
    db = get_db()
    skip = (page - 1) * limit
    total = await db.audio_files.count_documents({})
    cursor = db.audio_files.find({}).sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    pages = ceil(total / limit) if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
    }


@router.post("/audio/cleanup")
async def cleanup_unused_audio(admin: dict = Depends(get_current_admin)):
    """Delete audio files not referenced by any music track"""
    db = get_db()

    # Collect all audio paths used in tracks
    used_paths = set()
    async for music in db.music.find({}, {"tracks": 1}):
        for track in music.get("tracks", []):
            for key in ["audio_original", "audio_opus", "audio_mp3_320", "audio_mp3_128"]:
                val = track.get(key)
                if val:
                    used_paths.add(val)

    deleted_count = 0
    errors = []
    async for audio in db.audio_files.find({}):
        # Check if any of its paths are used
        in_use = any(
            audio.get(k) and audio[k] in used_paths
            for k in ["original_path", "opus_path", "mp3_320_path", "mp3_128_path"]
        )
        if not in_use:
            try:
                for key in ["original_path", "mp3_320_path", "mp3_128_path", "opus_path"]:
                    path_val = audio.get(key)
                    if path_val:
                        file_path = UPLOAD_DIR / path_val
                        if file_path.exists():
                            file_path.unlink()
                await db.audio_files.delete_one({"_id": audio["_id"]})
                deleted_count += 1
            except Exception as e:
                errors.append({"id": str(audio["_id"]), "error": str(e)})

    return {"deleted_count": deleted_count, "errors": errors}
