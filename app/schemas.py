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

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

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

# tags
class TagCreate(BaseModel):
    name: str

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
    original_price: float = 0.0
    price: float = 0.0
    is_free: bool = True
    developer: Optional[str] = None
    publisher: Optional[str] = None
    rating: Optional[str] = None
    requirements: Optional[str] = None
    meta_info: Optional[str] = None
    tag_ids: Optional[List[int]] = []

class GameUpdate(BaseModel):
    title: Optional[str] = None
    description_md: Optional[str] = None
    original_price: Optional[float] = None
    price: Optional[float] = None
    is_free: Optional[bool] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    rating: Optional[str] = None
    requirements: Optional[str] = None
    meta_info: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class GameOut(BaseModel):
    id: int
    title: str
    description_md: str
    original_price: float
    price: float
    is_free: bool
    developer: Optional[str] = None
    publisher: Optional[str] = None
    rating: Optional[str] = None
    requirements: Optional[str] = None
    meta_info: Optional[str] = None
    created_at: datetime
    tags: List[TagOut] = []
    banners: List[GameBannerOut] = []
    media: List[GameMediaOut] = []

    class Config:
        from_attributes = True

class GameListOut(BaseModel):
    id: int
    title: str
    original_price: float
    price: float
    is_free: bool
    developer: Optional[str] = None
    publisher: Optional[str] = None
    created_at: datetime
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
    game_id: int
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
    username: str

    class Config:
        from_attributes = True


# discussion schemas
class DiscussionCreate(BaseModel):
    game_id: int
    title: str
    content_md: str

class DiscussionUpdate(BaseModel):
    title: Optional[str] = None
    content_md: Optional[str] = None

class DiscussionOut(BaseModel):
    id: int
    game_id: int
    author_id: int
    thread_id: int
    title: str
    content_md: str
    created_at: datetime
    username: str

    class Config:
        from_attributes = True

# comment schemas
class CommentCreate(BaseModel):
    content_md: str

class CommentOut(BaseModel):
    id: int
    thread_id: int
    author_id: int
    content_md: str
    created_at: datetime
    username: str

    class Config:
        from_attributes = True

# thread schemas
class CommentThreadOut(BaseModel):
    id: int
    is_closed: bool
    created_at: datetime

    class Config:
        from_attributes = True
