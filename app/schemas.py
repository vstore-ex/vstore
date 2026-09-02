from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.game import MediaType, BannerType

# user schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_name: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# genres n tags
class GenreOut(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

class TagOut(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

# game media n banner schemas
class GameBannerOut(BaseModel):
    id: int
    banner_type: BannerType
    image_url: str

    class Config:
        from_attributes = True

class GameMediaOut(BaseModel):
    id: int
    media_type: MediaType
    url: str
    sort_order: int

    class Config:
        from_attributes = True

# game schemas
class GameCreate(BaseModel):
    title: str
    description_md: str
    price: float = 0.0
    is_free: bool = True
    developer: Optional[str] = None
    publisher: Optional[str] = None
    genre_ids: Optional[List[int]] = []
    tag_ids: Optional[List[int]] = []

class GameUpdate(BaseModel):
    title: Optional[str] = None
    description_md: Optional[str] = None
    price: Optional[float] = None
    is_free: Optional[bool] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    genre_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None

class GameOut(BaseModel):
    id: int
    title: str
    description_md: str
    price: float
    is_free: bool
    developer: Optional[str] = None
    publisher: Optional[str] = None
    created_at: datetime
    genres: List[GenreOut] = []
    tags: List[TagOut] = []
    banners: List[GameBannerOut] = []
    media: List[GameMediaOut] = []

    class Config:
        from_attributes = True

class GameListOut(BaseModel):
    id: int
    title: str
    price: float
    is_free: bool
    developer: Optional[str] = None
    publisher: Optional[str] = None
    created_at: datetime
    genres: List[GenreOut] = []
    tags: List[TagOut] = []
    banners: List[GameBannerOut] = []

    class Config:
        from_attributes = True

# review schemas
class ReviewCreate(BaseModel):
    is_positive: bool
    content_md: str

class ReviewUpdate(BaseModel):
    is_positive: Optional[bool] = None
    content_md: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    game_id: int
    user_id: int
    thread_id: int
    is_positive: bool
    content_md: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    username: str

    class Config:
        from_attributes = True

# artwork schemas
class ArtworkCreate(BaseModel):
    title: str
    image_url: str
    description_md: Optional[str] = None

class ArtworkUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    description_md: Optional[str] = None

class ArtworkOut(BaseModel):
    id: int
    game_id: int
    author_id: int
    thread_id: int
    title: str
    image_url: str
    description_md: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True