from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query, Body, Response
from bson import ObjectId
from datetime import datetime
from pathlib import Path
from PIL import Image
import uuid
import aiofiles
from database import get_db
from config import settings
from auth import get_current_user, get_optional_user
from routers.presence import invalidate_profile_cache

router = APIRouter(prefix="/api/profile", tags=["profile"])

UPLOAD_DIR = Path(settings.upload_dir)
AVATAR_DIR = UPLOAD_DIR / "avatars"
AVATAR_ORIGINAL = AVATAR_DIR / "original"
AVATAR_THUMB = AVATAR_DIR / "thumb"
BANNER_DIR = UPLOAD_DIR / "banners"
BANNER_ORIGINAL = BANNER_DIR / "original"
BANNER_THUMB = BANNER_DIR / "thumb"

for d in [AVATAR_ORIGINAL, AVATAR_THUMB, BANNER_ORIGINAL, BANNER_THUMB]:
    d.mkdir(parents=True, exist_ok=True)

AVATAR_THUMB_SIZE = (128, 128)
AVATAR_MAX_SIZE = 5 * 1024 * 1024  # 5MB
BANNER_MAX_SIZE = 10 * 1024 * 1024  # 10MB
BANNER_THUMB_SIZE = (1920, 600)
BIO_MAX_LENGTH = 190
NAME_MAX_LENGTH = 50

def serialize_profile(user: dict) -> dict:
    """Return public profile data"""
    return {
        "_id": str(user["_id"]),
        "username": user.get("username", ""),
        "display_name": user.get("display_name", ""),
        "bio": user.get("bio", ""),
        "avatar_original": user.get("avatar_original"),
        "avatar_thumb": user.get("avatar_thumb"),
        "banner_image": user.get("banner_image"),
        "role": user.get("role", "user"),
        "created_at": user.get("created_at"),
    }


@router.get("/me")
async def get_my_profile(user: dict = Depends(get_current_user)):
    return serialize_profile(user)


@router.get("/{username}")
async def get_profile(username: str):
    db = get_db()
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(404, "User not found")
    return serialize_profile(user)


@router.put("/me")
async def update_profile(
    user: dict = Depends(get_current_user),
    display_name: str = Body(None, embed=True),
    bio: str = Body(None, embed=True),
):
    db = get_db()
    update = {}

    if display_name is not None:
        if len(display_name) > NAME_MAX_LENGTH:
            raise HTTPException(400, f"Name too long (max {NAME_MAX_LENGTH} chars)")
        update["display_name"] = display_name.strip()

    if bio is not None:
        # count words
        words = bio.strip().split()
        if len(words) > BIO_MAX_LENGTH:
            raise HTTPException(400, f"Bio too long (max {BIO_MAX_LENGTH} words)")
        if len(bio) > 1500:
            raise HTTPException(400, "Bio text too long")
        update["bio"] = bio.strip()

    if not update:
        raise HTTPException(400, "Nothing to update")

    await db.users.update_one({"_id": user["_id"]}, {"$set": update})
    updated = await db.users.find_one({"_id": user["_id"]})
    return serialize_profile(updated)


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    crop_x: int = Query(0, description="Crop X offset"),
    crop_y: int = Query(0, description="Crop Y offset"),
    crop_size: int = Query(0, description="Crop square size (0 = auto)"),
    user: dict = Depends(get_current_user),
):
    """Upload avatar with optional crop coordinates"""
    db = get_db()

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in {"jpg", "jpeg", "png", "gif", "webp"}:
        raise HTTPException(400, "Only jpg, png, gif, webp allowed")

    content = await file.read()
    if len(content) > AVATAR_MAX_SIZE:
        raise HTTPException(400, "File too large (max 5MB)")

    uid = uuid.uuid4().hex[:10]
    original_name = f"{user['username']}_{uid}.{ext}"
    thumb_name = f"{user['username']}_{uid}_thumb.webp"

    original_path = AVATAR_ORIGINAL / original_name
    thumb_path = AVATAR_THUMB / thumb_name

    # Save original
    async with aiofiles.open(original_path, "wb") as f:
        await f.write(content)

    # Open and crop
    with Image.open(original_path) as img:
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (18, 18, 18))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size

        if crop_size > 0:
            # Apply crop
            cx = max(0, min(crop_x, w - 1))
            cy = max(0, min(crop_y, h - 1))
            cs = max(1, min(crop_size, w - cx, h - cy))
            cropped = img.crop((cx, cy, cx + cs, cy + cs))
        else:
            # Auto center-crop to square
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            cropped = img.crop((left, top, left + side, top + side))

        # Save original (re-save after potential convert)
        img.save(original_path, quality=90)

        # Create thumb
        cropped.thumbnail(AVATAR_THUMB_SIZE, Image.Resampling.LANCZOS)
        cropped.save(thumb_path, "WEBP", quality=85, method=6)

    # Delete old avatars
    old_original = user.get("avatar_original")
    old_thumb = user.get("avatar_thumb")
    if old_original:
        old_path = UPLOAD_DIR / old_original
        if old_path.exists():
            old_path.unlink(missing_ok=True)
    if old_thumb:
        old_path = UPLOAD_DIR / old_thumb
        if old_path.exists():
            old_path.unlink(missing_ok=True)

    avatar_original = f"avatars/original/{original_name}"
    avatar_thumb = f"avatars/thumb/{thumb_name}"

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"avatar_original": avatar_original, "avatar_thumb": avatar_thumb}},
    )

    # FIX: инвалидируем кэш presence
    await invalidate_profile_cache(str(user["_id"]))
    return {
        "avatar_original": avatar_original,
        "avatar_thumb": avatar_thumb,
    }


@router.delete("/me/avatar")
async def delete_avatar(user: dict = Depends(get_current_user)):
    db = get_db()
    old_original = user.get("avatar_original")
    old_thumb = user.get("avatar_thumb")
    if old_original:
        p = UPLOAD_DIR / old_original
        if p.exists():
            p.unlink(missing_ok=True)
    if old_thumb:
        p = UPLOAD_DIR / old_thumb
        if p.exists():
            p.unlink(missing_ok=True)

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"avatar_original": None, "avatar_thumb": None}},
    )
    # FIX: инвалидируем кэш presence
    await invalidate_profile_cache(str(user["_id"]))
    return {"deleted": True}


@router.post("/me/banner")
async def upload_banner(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Upload profile banner image"""
    db = get_db()

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in {"jpg", "jpeg", "png", "gif", "webp"}:
        raise HTTPException(400, "Only jpg, png, gif, webp allowed")

    content = await file.read()
    if len(content) > BANNER_MAX_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")

    uid = uuid.uuid4().hex[:10]
    original_name = f"{user['username']}_banner_{uid}.{ext}"
    thumb_name = f"{user['username']}_banner_{uid}_thumb.webp"

    original_path = BANNER_ORIGINAL / original_name
    thumb_path = BANNER_THUMB / thumb_name

    # Save original
    async with aiofiles.open(original_path, "wb") as f:
        await f.write(content)

    # Process image
    with Image.open(original_path) as img:
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (18, 18, 18))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Save original
        img.save(original_path, quality=90)

        # Create thumb (resize to banner dimensions)
        thumb_img = img.copy()
        thumb_img.thumbnail(BANNER_THUMB_SIZE, Image.Resampling.LANCZOS)
        thumb_img.save(thumb_path, "WEBP", quality=85, method=6)

    # Delete old banner
    old_banner = user.get("banner_image")
    if old_banner:
        old_path = UPLOAD_DIR / old_banner
        if old_path.exists():
            old_path.unlink(missing_ok=True)
        old_thumb_path = UPLOAD_DIR / old_banner.replace("original", "thumb").replace(ext, "webp")
        if old_thumb_path.exists():
            old_thumb_path.unlink(missing_ok=True)

    banner_original = f"banners/original/{original_name}"
    banner_thumb = f"banners/thumb/{thumb_name}"

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"banner_image": banner_original}},
    )

    # FIX: инвалидируем кэш presence
    await invalidate_profile_cache(str(user["_id"]))
    return {
        "banner_image": banner_original,
    }


@router.delete("/me/banner")
async def delete_banner(user: dict = Depends(get_current_user)):
    db = get_db()
    old_banner = user.get("banner_image")
    if old_banner:
        p = UPLOAD_DIR / old_banner
        if p.exists():
            p.unlink(missing_ok=True)
        # Delete thumb by pattern
        for f in BANNER_THUMB.glob(f"{user['username']}_banner_*_thumb.webp"):
            f.unlink(missing_ok=True)

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"banner_image": None}},
    )
    # FIX: инвалидируем кэш presence
    await invalidate_profile_cache(str(user["_id"]))
    return {"deleted": True}
