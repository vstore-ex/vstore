from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Discussion(Base):
    __tablename__ = "discussions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("comment_threads.id"), nullable=False, unique=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    # article content (markdown with images)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    game: Mapped["Game"] = relationship("Game", back_populates="discussions")
    author: Mapped["User"] = relationship("User")
    thread: Mapped["CommentThread"] = relationship("CommentThread", cascade="all, delete-orphan", single_parent=True)