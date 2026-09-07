from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.db import get_db
from app.models import User, Game, UserWishlist
from app.schemas import WishlistResponse, WishlistItemOut
from app.api.auth.authorization import get_current_user

router = APIRouter(prefix="/wishlists", tags=["wishlists"])

@router.get("/", response_model=WishlistResponse)
async def get_my_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(UserWishlist).options(
        joinedload(UserWishlist.product)
    ).filter(UserWishlist.user_id == current_user.id).all()

    return WishlistResponse(items=items)

@router.post("/{game_id}", status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    # check if already in wishlist
    existing = db.query(UserWishlist).filter(
        UserWishlist.user_id == current_user.id,
        UserWishlist.product_id == game_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="game already in wishlist")

    wishlist_item = UserWishlist(user_id=current_user.id, product_id=game_id)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)

    return {"message": "game added to wishlist"}

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(UserWishlist).filter(
        UserWishlist.user_id == current_user.id,
        UserWishlist.product_id == game_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="game not found in wishlist")

    db.delete(item)
    db.commit()

    return None

@router.get("/count")
async def get_wishlist_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = db.query(UserWishlist).filter(UserWishlist.user_id == current_user.id).count()
    return {"count": count}