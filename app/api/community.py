from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.models import Game, User
from app.models.discussion import Discussion
from app.models.comment import Comment, CommentThread
from app.schemas import DiscussionCreate, DiscussionUpdate, DiscussionOut, CommentCreate, CommentOut, CommentThreadOut
from app.api.auth.authorization import get_current_user, require_admin
from app.services.markdown import markdown_service

router = APIRouter(prefix="/community", tags=["community"])

# discussions

@router.get("/discussions", response_model=List[DiscussionOut])
async def list_discussions(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    discussions = db.query(Discussion).offset(skip).limit(limit).all()

    result = []
    for d in discussions:
        data = d.__dict__.copy()
        data["username"] = d.author.username
        result.append(DiscussionOut(**data))
    return result

@router.get("/games/{game_id}/discussions", response_model=List[DiscussionOut])
async def list_game_discussions(game_id: int, db: Session = Depends(get_db)):
    discussions = db.query(Discussion).filter(Discussion.game_id == game_id).all()

    result = []
    for d in discussions:
        data = d.__dict__.copy()
        data["username"] = d.author.username
        result.append(DiscussionOut(**data))
    return result

@router.get("/discussions/{discussion_id}", response_model=DiscussionOut)
async def get_discussion(discussion_id: int, db: Session = Depends(get_db)):
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="discussion not found")

    data = discussion.__dict__.copy()
    data["username"] = discussion.author.username
    return DiscussionOut(**data)

@router.post("/discussions", response_model=DiscussionOut, status_code=status.HTTP_201_CREATED)
async def create_discussion(
    discussion_in: DiscussionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # validate game exists
    game = db.query(Game).filter(Game.id == discussion_in.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    # create thread
    thread = CommentThread()
    db.add(thread)
    db.flush()

    processed_md = await markdown_service.process_content(
        discussion_in.content_md,
        allow_images=True
    )

    discussion = Discussion(
        game_id=discussion_in.game_id,
        author_id=current_user.id,
        thread_id=thread.id,
        title=discussion_in.title,
        content_md=processed_md
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)

    data = discussion.__dict__.copy()
    data["username"] = current_user.username
    return DiscussionOut(**data)

@router.put("/discussions/{discussion_id}", response_model=DiscussionOut)
async def update_discussion(
    discussion_id: int,
    discussion_in: DiscussionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="discussion not found")

    if discussion.author_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")

    if discussion_in.title is not None:
        discussion.title = discussion_in.title
    if discussion_in.content_md is not None:
        discussion.content_md = await markdown_service.process_content(
            discussion_in.content_md,
            allow_images=True
        )

    db.commit()
    db.refresh(discussion)

    data = discussion.__dict__.copy()
    data["username"] = discussion.author.username
    return DiscussionOut(**data)

@router.delete("/discussions/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="discussion not found")

    if discussion.author_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")

    db.delete(discussion)
    db.commit()
    return None

# comms

@router.get("/threads/{thread_id}/comments", response_model=List[CommentOut])
async def list_comments(thread_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    thread = db.query(CommentThread).filter(CommentThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="thread not found")

    comments = db.query(Comment).filter(Comment.thread_id == thread_id).offset(skip).limit(limit).all()

    result = []
    for c in comments:
        data = c.__dict__.copy()
        data["username"] = c.author.username
        result.append(CommentOut(**data))
    return result

@router.post("/threads/{thread_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    thread_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(CommentThread).filter(CommentThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="thread not found")

    if thread.is_closed:
        raise HTTPException(status_code=400, detail="thread is closed")

    # no images allowed
    processed_md = await markdown_service.process_content(
        comment_in.content_md,
        allow_images=False
    )

    comment = Comment(
        thread_id=thread_id,
        author_id=current_user.id,
        content_md=processed_md
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    data = comment.__dict__.copy()
    data["username"] = current_user.username
    return CommentOut(**data)

@router.put("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="comment not found")

    if comment.author_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")

    comment.content_md = await markdown_service.process_content(
        comment_in.content_md,
        allow_images=False
    )
    db.commit()
    db.refresh(comment)
    data = comment.__dict__.copy()
    data["username"] = comment.author.username
    return CommentOut(**data)

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="comment not found")

    if comment.author_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")
    db.delete(comment)
    db.commit()
    return None