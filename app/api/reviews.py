from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.models import Game, GameReview, CommentThread, User, ReviewReaction, ReactionType
from app.schemas import ReviewCreate, ReviewUpdate, ReviewOut, ReviewVoteRequest
from app.api.auth.authorization import get_current_user
from app.services.markdown import markdown_service

router = APIRouter(tags=["reviews"])

# game scoped

@router.get("/games/{game_id}/reviews", response_model=List[ReviewOut])
async def list_reviews(
    game_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    reviews = (
        db.query(GameReview)
        .options(joinedload(GameReview.user))
        .filter(GameReview.game_id == game_id, GameReview.is_hidden == False)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for r in reviews:
        data = r.__dict__.copy()
        data["username"] = r.user.username
        result.append(ReviewOut(**data))
    return result

@router.post("/games/{game_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(
    game_id: int,
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    existing = db.query(GameReview).filter(
        GameReview.game_id == game_id,
        GameReview.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="already reviewed")

    thread = CommentThread()
    db.add(thread)
    db.flush()

    processed_content = await markdown_service.process_content(review_in.content_md, allow_images=False)

    review = GameReview(
        game_id=game_id,
        user_id=current_user.id,
        thread_id=thread.id,
        is_positive=review_in.is_positive,
        content_md=processed_content
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    data = review.__dict__.copy()
    data["username"] = current_user.username
    return ReviewOut(**data)

# global review endpoints

@router.patch("/reviews/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: int,
    review_in: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(GameReview).options(joinedload(GameReview.user)).filter(
        GameReview.id == review_id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="review not found")

    if review.user_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")

    if review_in.is_positive is not None:
        review.is_positive = review_in.is_positive

    if review_in.content_md is not None:
        review.content_md = await markdown_service.process_content(review_in.content_md, allow_images=False)
        review.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(review)

    data = review.__dict__.copy()
    data["username"] = review.user.username
    return ReviewOut(**data)

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(GameReview).filter(GameReview.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="review not found")

    if review.user_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")

    db.delete(review)
    db.commit()
    return None

@router.post("/reviews/{review_id}/vote", status_code=status.HTTP_201_CREATED)
async def vote_review(
    review_id: int,
    vote_in: ReviewVoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(GameReview).filter(GameReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="review not found")

    # check if user already voted on this review with this type
    existing_vote = db.query(ReviewReaction).filter(
        ReviewReaction.review_id == review_id,
        ReviewReaction.user_id == current_user.id,
        ReviewReaction.reaction_type == vote_in.reaction_type
    ).first()

    if existing_vote:
        # toggle vote. remove if exists
        db.delete(existing_vote)
        db.commit()
        return {"message": "vote removed"}

    # create new vote
    vote = ReviewReaction(
        review_id=review_id,
        user_id=current_user.id,
        reaction_type=vote_in.reaction_type
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)

    return {"message": "vote added", "reaction": vote.reaction_type}