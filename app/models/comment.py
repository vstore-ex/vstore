from datetime import datetime
from sqlalchemy import Integer, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

# comment thread container for any entity
class CommentThread(Base):
    __tablename__ = "comment_threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="thread", cascade="all, delete-orphan")

# single comment item (markdown, no images)
class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("comment_threads.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    thread: Mapped["CommentThread"] = relationship("CommentThread", back_populates="comments")
    author: Mapped["User"] = relationship("User")