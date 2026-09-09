from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.core.db import get_db
from app.models.user import User, Role
from app.models.review import GameReview
from app.models.achievement import UserAchievement
from app.models.wishlist import UserWishlist
from app.schemas import UserOut, UserUpdate, UserStats
from app.api.auth.authorization import get_current_user, require_admin
from app.services.media import media_service

router = APIRouter(prefix="/users", tags=["users"])

def get_user_stats(db: Session, user_id: int) -> UserStats:
    games_count = db.query(GameReview).filter(GameReview.user_id == user_id).count()
    achievements_count = db.query(UserAchievement).filter(UserAchievement.user_id == user_id).count()
    wishlist_count = db.query(UserWishlist).filter(UserWishlist.user_id == user_id).count()
    return UserStats(
        games=games_count,
        achievements=achievements_count,
        wishlist=wishlist_count
    )

def get_users_stats_map(db: Session, user_ids: List[int]) -> Dict[int, UserStats]:
    if not user_ids:
        return {}
    games_counts = dict(
        db.query(GameReview.user_id, func.count(GameReview.id))
        .filter(GameReview.user_id.in_(user_ids))
        .group_by(GameReview.user_id)
        .all()
    )
    achievements_counts = dict(
        db.query(UserAchievement.user_id, func.count(UserAchievement.id))
        .filter(UserAchievement.user_id.in_(user_ids))
        .group_by(UserAchievement.user_id)
        .all()
    )
    wishlist_counts = dict(
        db.query(UserWishlist.user_id, func.count(UserWishlist.id))
        .filter(UserWishlist.user_id.in_(user_ids))
        .group_by(UserWishlist.user_id)
        .all()
    )
    return {
        uid: UserStats(
            games=games_counts.get(uid, 0),
            achievements=achievements_counts.get(uid, 0),
            wishlist=wishlist_counts.get(uid, 0)
        )
        for uid in user_ids
    }


# explicit model fields
def build_user_out(user: User, stats: UserStats) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        avatar=user.avatar,
        is_banned=user.is_banned,
        created_at=user.created_at,
        role_name=user.role.name if user.role else "",
        stats=stats
    )

@router.get("/", response_model=List[UserOut])
async def list_public_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .options(joinedload(User.role))
        .offset(skip)
        .limit(limit)
        .all()
    )
    stats_map = get_users_stats_map(db, [u.id for u in users])
    return [build_user_out(u, stats_map.get(u.id, UserStats())) for u in users]

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = get_user_stats(db, current_user.id)
    return build_user_out(current_user, stats)

@router.get("/{user_id}", response_model=UserOut)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    stats = get_user_stats(db, user.id)
    return build_user_out(user, stats)

@router.patch("/me", response_model=UserOut)
async def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    stats = get_user_stats(db, current_user.id)
    return build_user_out(current_user, stats)

@router.patch("/me/avatar", response_model=UserOut)
async def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="file must be an image")

    try:
        file_bytes = await file.read()
        webp_bytes = media_service.convert_to_webp(file_bytes)
        filename = f"avatar_{current_user.id}.webp"
        url = media_service.upload_bytes(webp_bytes, filename, content_type="image/webp")

        current_user.avatar = url
        db.commit()
        db.refresh(current_user)

        stats = get_user_stats(db, current_user.id)
        return build_user_out(current_user, stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"avatar upload failed: {str(e)}")

# admin

@router.get("/admin", response_model=List[UserOut])
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    users = (
        db.query(User)
        .options(joinedload(User.role))
        .offset(skip)
        .limit(limit)
        .all()
    )
    stats_map = get_users_stats_map(db, [u.id for u in users])
    return [build_user_out(u, stats_map.get(u.id, UserStats())) for u in users]

@router.put("/admin/{user_id}", response_model=UserOut)
async def update_user_admin(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    stats = get_user_stats(db, user.id)
    return build_user_out(user, stats)

@router.post("/admin/{user_id}/toggle-ban")
async def toggle_user_ban(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    if user.is_admin:
        raise HTTPException(status_code=403, detail="cannot ban admin")

    user.is_banned = not user.is_banned
    db.commit()
    db.refresh(user)

    status_text = "banned" if user.is_banned else "unbanned"
    return {
        "message": f"user {user.username} has been {status_text}",
        "is_banned": user.is_banned
    }

@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    db.delete(user)
    db.commit()
    return None