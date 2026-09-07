from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from typing import Optional
from datetime import datetime
from app.models.base import Base

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    can_buy: Mapped[bool] = mapped_column(default=True, nullable=False)
    can_message: Mapped[bool] = mapped_column(default=True, nullable=False)
    can_ban: Mapped[bool] = mapped_column(default=False, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role(name={self.name})>"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    unlocked_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    wishlist_items: Mapped[list["UserWishlist"]] = relationship("UserWishlist", back_populates="user", cascade="all, delete-orphan")
    cart_items: Mapped[list["UserCart"]] = relationship("UserCart", back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")