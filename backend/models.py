from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# SEO Model for reuse
class SEOFields(BaseModel):
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=200)
    og_image: Optional[str] = None  # Image ID for Open Graph

class TrackItem(BaseModel):
    number: int = Field(..., ge=1, le=999)
    title: str = Field(..., min_length=1, max_length=200)
    duration: str = Field(default="00:00", pattern=r'^\d{1,2}:\d{2}$')
    audio_original: Optional[str] = None   # Original uploaded file ID (FLAC/MP3)
    audio_mp3_320: Optional[str] = None    # MP3 320kbps file path
    audio_mp3_128: Optional[str] = None    # MP3 128kbps file path (optional)
    audio_opus: Optional[str] = None       # Opus 128kbps file path (for player)
    has_mp3_128: bool = False              # Whether to generate MP3 128kbps

class GalleryImage(BaseModel):
    image_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)  # Custom name for the image (used for filename)

class MusicReleaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = Field(None, max_length=250, pattern=r'^[a-z0-9-]+$')  # URL slug
    release_date: datetime
    genre: str = Field(..., min_length=1, max_length=100)
    release_type: str = Field(default="Album", max_length=50)
    price: str = Field(default="Name your price", max_length=100)
    tracks: List[TrackItem] = Field(default=[], max_length=100)  # Max 100 tracks
    gallery: List[GalleryImage] = Field(default=[], max_length=50)  # Max 50 gallery images
    cover_image: Optional[str] = None  # Image ID
    description: Optional[str] = Field(None, max_length=5000)
    bandcamp_url: Optional[str] = Field(None, max_length=500)
    is_new: bool = False
    production_notes: Optional[str] = Field(None, max_length=5000)
    liner_notes: Optional[str] = Field(None, max_length=10000)
    download_mp3: Optional[str] = Field(None, max_length=500)
    download_flac: Optional[str] = Field(None, max_length=500)
    # SEO fields
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=200)
    og_image: Optional[str] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = Field(None, max_length=250, pattern=r'^[a-z0-9-]+$')  # URL slug
    content: str = Field(..., min_length=1, max_length=100000)  # Markdown content (max 100k chars)
    excerpt: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = None  # Image ID
    # SEO fields
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=200)
    og_image: Optional[str] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

class ArtWorkCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = Field(None, max_length=250, pattern=r'^[a-z0-9-]+$')  # URL slug
    description: Optional[str] = Field(None, max_length=2000)  # Markdown content
    image: Optional[str] = None  # Image ID (original)
    dimensions: str = Field(default="1024 x 1024", max_length=50)
    file_size: str = Field(default="1.2 MB", max_length=50)
    year: int = Field(..., ge=1900, le=2100)
    # SEO fields
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=200)
    og_image: Optional[str] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

class BannerSlide(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    image: str = Field(..., min_length=1)  # Image ID
    link: Optional[str] = Field(None, max_length=500)
    order: int = Field(default=0, ge=0, le=999)

class BannerCreate(BaseModel):
    slides: List[BannerSlide] = Field(default=[], max_length=20)  # Max 20 slides

class ImageInfo(BaseModel):
    id: str
    original: str
    thumb: str
    medium: str
    filename: str
    size: int
    width: int
    height: int
    created_at: datetime
    category: Optional[str] = None  # music, blog, arts, markdown
    parent_id: Optional[str] = None  # ID of the parent entity
    custom_name: Optional[str] = None  # Custom name for the file

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool

# View tracking for analytics
class ViewRecord(BaseModel):
    entity_type: str  # music, blog, arts
    entity_id: str
    date: datetime
    count: int = 1
