import math
import re
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.db import get_db
from app.models import Game, Achievement, User
from app.models.achievement import UserAchievement
from app.schemas import (
    AchievementCreate,
    AchievementUpdate,
    AchievementOut,
    AchievementPaginatedResponse,
)
from app.api.auth.authorization import require_admin, get_current_user, get_optional_current_user

router = APIRouter(tags=["achievements"])

def slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'[^a-z0-9-]', '', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

def get_game_or_404(db: Session, product_id: str) -> Game:
    if product_id.isdigit():
        game = db.query(Game).filter(Game.id == int(product_id)).first()
        if game:
            return game
    game = db.query(Game).filter(Game.title.ilike(product_id.replace('-', ' '))).first()
    if not game:
        raise HTTPException(status_code=404, detail="product not found")
    return game

@router.get("/products/{id}/achievements", response_model=AchievementPaginatedResponse)
async def list_product_achievements(
    id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(11, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    game = get_game_or_404(db, id)
    query = db.query(Achievement).filter(Achievement.product_id == game.id)
    total = query.count()

    total_pages = math.ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size

    items = query.offset(offset).limit(page_size).all()

    user_unlocked_map: Dict[str, UserAchievement] = {}
    user_completion_percent: Optional[float] = None

    if current_user:
        unlocked_records = (
            db.query(UserAchievement)
            .join(Achievement, UserAchievement.achievement_id == Achievement.id)
            .filter(
                UserAchievement.user_id == current_user.id,
                Achievement.product_id == game.id
            )
            .all()
        )
        user_unlocked_map = {ua.achievement_id: ua for ua in unlocked_records}
        if total > 0:
            user_completion_percent = round((len(unlocked_records) / total) * 100, 2)
        else:
            user_completion_percent = 0.0

    result_items = []
    for ach in items:
        unlocked_rec = user_unlocked_map.get(ach.id)
        result_items.append(
            AchievementOut(
                id=ach.id,
                product_id=ach.product_id,
                title=ach.title,
                description=ach.description,
                icon=ach.icon,
                completion_percent=ach.completion_percent,
                unlocked=bool(unlocked_rec) if current_user else None,
                unlocked_at=unlocked_rec.unlocked_at if unlocked_rec else None
            )
        )

    return AchievementPaginatedResponse(
        items=result_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        user_completion_percent=user_completion_percent
    )

@router.post("/achievements/{id}/unlock", status_code=status.HTTP_200_OK)
async def unlock_achievement(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    achievement = db.query(Achievement).filter(Achievement.id == id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="achievement not found")

    existing = (
        db.query(UserAchievement)
        .filter(
            UserAchievement.user_id == current_user.id,
            UserAchievement.achievement_id == achievement.id
        )
        .first()
    )
    if not existing:
        user_ach = UserAchievement(
            user_id=current_user.id,
            achievement_id=achievement.id
        )
        db.add(user_ach)
        db.commit()

        # recalculate global completion_percent for this achievement
        total_users = db.query(func.count(User.id)).scalar() or 1
        unlocked_count = db.query(func.count(UserAchievement.id)).filter(UserAchievement.achievement_id == achievement.id).scalar() or 0
        achievement.completion_percent = round((unlocked_count / total_users) * 100, 2)
        db.commit()

    return {"message": "achievement unlocked", "achievement_id": achievement.id}

@router.post("/admin/products/{id}/achievements", response_model=AchievementOut, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    id: str,
    achievement_in: AchievementCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    game = get_game_or_404(db, id)

    achievement_id = achievement_in.id
    if not achievement_id:
        achievement_id = slugify(achievement_in.title)

    if not achievement_id:
        raise HTTPException(status_code=400, detail="invalid achievement id")

    existing = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="achievement id already exists")

    achievement = Achievement(
        id=achievement_id,
        product_id=game.id,
        title=achievement_in.title,
        description=achievement_in.description,
        icon=achievement_in.icon,
        completion_percent=achievement_in.completion_percent
    )
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement

@router.patch("/admin/achievements/{id}", response_model=AchievementOut)
async def update_achievement(
    id: str,
    achievement_in: AchievementUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    achievement = db.query(Achievement).filter(Achievement.id == id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="achievement not found")

    update_data = achievement_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(achievement, field, value)

    db.commit()
    db.refresh(achievement)
    return achievement

@router.delete("/admin/achievements/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(
    id: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    achievement = db.query(Achievement).filter(Achievement.id == id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="achievement not found")

    db.delete(achievement)
    db.commit()
    return None