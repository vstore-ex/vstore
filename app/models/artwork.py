from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("comment_threads.id", ondelete="CASCADE"), nullable=False, unique=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description_md: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)

    game: Mapped["Game"] = relationship("Game", back_populates="artworks")
    author: Mapped["User"] = relationship("User")
    thread: Mapped["CommentThread"] = relationship("CommentThread", cascade="all, delete-orphan", single_parent=True)