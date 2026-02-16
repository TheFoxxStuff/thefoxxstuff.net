from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# SEO Model for reuse
class SEOFields(BaseModel):
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    og_image: Optional[str] = None  # Image ID for Open Graph

class TrackItem(BaseModel):
    number: int
    title: str
    duration: str = "00:00"
    audio_original: Optional[str] = None   # Original uploaded file ID (FLAC/MP3)
    audio_mp3_320: Optional[str] = None    # MP3 320kbps file path
    audio_mp3_128: Optional[str] = None    # MP3 128kbps file path (optional)
    audio_opus: Optional[str] = None       # Opus 128kbps file path (for player)
    has_mp3_128: bool = False              # Whether to generate MP3 128kbps

class GalleryImage(BaseModel):
    image_id: str
    name: str  # Custom name for the image (used for filename)

class MusicReleaseCreate(BaseModel):
    title: str
    slug: Optional[str] = None  # URL slug
    release_date: datetime
    genre: str
    release_type: str = "Album"
    price: str = "Name your price"
    tracks: List[TrackItem] = []
    gallery: List[GalleryImage] = []  # Updated to include name
    cover_image: Optional[str] = None  # Image ID
    description: Optional[str] = None
    bandcamp_url: Optional[str] = None
    is_new: bool = False
    production_notes: Optional[str] = None
    liner_notes: Optional[str] = None
    download_mp3: Optional[str] = None
    download_flac: Optional[str] = None
    # SEO fields
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    og_image: Optional[str] = None

class BlogPostCreate(BaseModel):
    title: str
    slug: Optional[str] = None  # URL slug
    content: str  # Markdown content
    excerpt: Optional[str] = None
    cover_image: Optional[str] = None  # Image ID
    # SEO fields
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    og_image: Optional[str] = None

class ArtWorkCreate(BaseModel):
    title: str
    slug: Optional[str] = None  # URL slug
    description: Optional[str] = None  # Markdown content
    image: Optional[str] = None  # Image ID (original)
    dimensions: str = "1024 x 1024"
    file_size: str = "1.2 MB"
    year: int
    # SEO fields
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    og_image: Optional[str] = None

class LinkCreate(BaseModel):
    title: str
    url: str
    icon: Optional[str] = None
    order: int = 0

class BannerSlide(BaseModel):
    title: str
    image: str  # Image ID
    link: Optional[str] = None
    order: int = 0

class BannerCreate(BaseModel):
    slides: List[BannerSlide] = []

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
