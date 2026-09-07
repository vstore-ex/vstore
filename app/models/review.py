from enum import Enum as PyEnum
from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, Boolean, ForeignKey, Text, Enum, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ReactionType(str, PyEnum):
    HELPFUL = "helpful"
    FUNNY = "funny"

class GameReview(Base):
    __tablename__ = "game_reviews"
    __table_args__ = (UniqueConstraint("game_id", "user_id", name="uq_user_game_review"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("comment_threads.id", ondelete="CASCADE"), nullable=False, unique=True)

    is_positive: Mapped[bool] = mapped_column(Boolean, nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)

    game: Mapped["Game"] = relationship("Game", back_populates="reviews")
    user: Mapped["User"] = relationship("User")
    thread: Mapped["CommentThread"] = relationship("CommentThread", cascade="all, delete-orphan", single_parent=True)
    reactions: Mapped[list["ReviewReaction"]] = relationship("ReviewReaction", back_populates="review", cascade="all, delete-orphan")

class ReviewReaction(Base):
    __tablename__ = "review_reactions"
    __table_args__ = (UniqueConstraint("review_id", "user_id", "reaction_type", name="uq_user_review_reaction"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reaction_type: Mapped[ReactionType] = mapped_column(Enum(ReactionType), nullable=False)

    review: Mapped["GameReview"] = relationship("GameReview", back_populates="reactions")
    user: Mapped["User"] = relationship("User")