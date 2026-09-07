from enum import Enum as PyEnum
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text, Enum, UniqueConstraint, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.taxonomy import game_tags

class MediaType(str, PyEnum):
    IMAGE = "image"
    VIDEO = "video"

class BannerType(str, PyEnum):
    MAIN_HERO = "main_hero"
    SPECIAL_OFFER = "special_offer"
    SMALL_CAPSULE = "small_capsule"
    GAME_PAGE_HEADER = "game_page_header"
    LIBRARY_ICON = "library_icon"
    LIBRARY_POSTER = "library_poster"
    LIBRARY_HERO = "library_hero"
    COLLECTION_HEADER = "collection_header"

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description_md: Mapped[str] = mapped_column(Text, nullable=False)

    original_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    developer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rating: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    tags: Mapped[list["Tag"]] = relationship("Tag", secondary=game_tags, back_populates="games")
    media: Mapped[list["GameMedia"]] = relationship("GameMedia", back_populates="game", cascade="all, delete-orphan")
    banners: Mapped[list["GameBanner"]] = relationship("GameBanner", back_populates="game", cascade="all, delete-orphan")
    reviews: Mapped[list["GameReview"]] = relationship("GameReview", back_populates="game")
    discussions: Mapped[list["Discussion"]] = relationship("Discussion", back_populates="game")
    artworks: Mapped[list["Artwork"]] = relationship("Artwork", back_populates="game")
    achievements: Mapped[list["Achievement"]] = relationship("Achievement", back_populates="game", cascade="all, delete-orphan")
    wishlist_entries: Mapped[list["UserWishlist"]] = relationship("UserWishlist", back_populates="product", cascade="all, delete-orphan")
    cart_entries: Mapped[list["UserCart"]] = relationship("UserCart", back_populates="product", cascade="all, delete-orphan")

class GameBanner(Base):
    __tablename__ = "game_banners"
    __table_args__ = (UniqueConstraint("game_id", "banner_type", name="uq_game_banner_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    banner_type: Mapped[BannerType] = mapped_column(Enum(BannerType), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    game: Mapped["Game"] = relationship("Game", back_populates="banners")

class GameMedia(Base):
    __tablename__ = "game_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    game: Mapped["Game"] = relationship("Game", back_populates="media")