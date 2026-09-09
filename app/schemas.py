from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from decimal import Decimal
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
    avatar: Optional[str] = None

class UserAdminUpdate(UserUpdate):
    role_id: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserStats(BaseModel):
    games: int = 0
    achievements: int = 0
    wishlist: int = 0

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_banned: bool
    created_at: datetime
    role_name: str
    stats: UserStats = UserStats()

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# stats schemas
class StatPointOut(BaseModel):
    label: str
    value: int

class StatValueOut(BaseModel):
    label: str
    value: float

class TopItemOut(BaseModel):
    id: int
    title: str
    count: int

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
    thumbnail_url: Optional[str] = None
    sort_order: int

    class Config:
        from_attributes = True

# game schemas
class GameCreate(BaseModel):
    title: str
    description_md: str
    original_price: Decimal = Decimal("0.00")
    price: Decimal = Decimal("0.00")
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
    original_price: Optional[Decimal] = None
    price: Optional[Decimal] = None
    is_free: Optional[bool] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    rating: Optional[str] = None
    requirements: Optional[str] = None
    meta_info: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class GameAdminUpdate(GameUpdate):
    is_active: Optional[bool] = None

class GameOut(BaseModel):
    id: int
    title: str
    description_md: str
    original_price: Decimal
    price: Decimal
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
    original_price: Decimal
    price: Decimal
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

class ReviewVoteRequest(BaseModel):
    reaction_type: str

# cart schemas
class CartItemOut(BaseModel):
    product_id: int
    title: str
    price: Decimal
    added_at: datetime

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: List[CartItemOut]
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    currency: str = "UAH"

# order schemas
class OrderCreate(BaseModel):
    payment_method: str
    terms_accepted: bool

class OrderItemOut(BaseModel):
    product_id: int
    price_at_purchase: Decimal

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    status: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

# support schemas
class SupportArticleOut(BaseModel):
    id: int
    title: str
    content_md: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SupportArticlePaginatedResponse(BaseModel):
    items: List[SupportArticleOut]
    total: int
    page: int
    page_size: int
    total_pages: int

class SupportTicketCreate(BaseModel):
    subject: str
    message: str
    priority: Optional[str] = "medium"

class SupportTicketOut(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SupportTicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

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

# achievement schemas
class AchievementCreate(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    icon: str
    completion_percent: float = 0.0

class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    completion_percent: Optional[float] = None

class AchievementOut(BaseModel):
    id: str
    product_id: Union[int, str]
    title: str
    description: str
    icon: str
    completion_percent: float
    unlocked: Optional[bool] = None
    unlocked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AchievementPaginatedResponse(BaseModel):
    items: List[AchievementOut]
    total: int
    page: int
    page_size: int
    total_pages: int
    user_completion_percent: Optional[float] = None

# wishlist schemas
class WishlistItemOut(BaseModel):
    product: GameOut
    added_at: datetime

    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    items: List[WishlistItemOut]

# discover schemas
class DiscoverSectionOut(BaseModel):
    id: str
    title: str
    games: List[GameListOut]

class DiscoverPromoOut(BaseModel):
    id: str
    title: str
    image_url: str
    link: str

class DiscoverRankedColumnOut(BaseModel):
    title: str
    games: List[GameListOut]

class DiscoverLayoutOut(BaseModel):
    featured: Optional[GameListOut] = None
    sections: List[DiscoverSectionOut] = []
    promos: List[DiscoverPromoOut] = []
    deals: List[GameListOut] = []
    free_games: List[GameListOut] = []
    ranked_columns: List[DiscoverRankedColumnOut] = []
    mobile_banner: Optional[dict] = None

class DiscoverSectionUpdate(BaseModel):
    id: str
    title: str
    game_ids: List[int]

class DiscoverLayoutUpdate(BaseModel):
    featured_game_id: Optional[int] = None
    sections: Optional[List[DiscoverSectionUpdate]] = None
    promos: Optional[List[dict]] = None
    deals_game_ids: Optional[List[int]] = None
    free_games_game_ids: Optional[List[int]] = None
    ranked_columns: Optional[List[dict]] = None
    mobile_banner: Optional[dict] = None