from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Numeric, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(500), nullable=False)
    completion_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)

    game: Mapped["Game"] = relationship("Game", back_populates="achievements")
    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id: Mapped[str] = mapped_column(String(100), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="unlocked_achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")