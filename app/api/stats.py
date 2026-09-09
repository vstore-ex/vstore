from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.core.db import get_db
from app.api.auth.authorization import require_admin
from app.models import User, GameReview, Order, Game
from app.schemas import StatPointOut, StatValueOut, TopItemOut

router = APIRouter(prefix="/stats", tags=["stats"])

# public stats

@router.get("/reviews-activity", response_model=List[StatPointOut])
async def get_reviews_activity(
    db: Session = Depends(get_db)
):
    # returns number of reviews per day for the last 15 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=15)

    results = (
        db.query(
            func.date(GameReview.created_at).label("date"),
            func.count(GameReview.id).label("count")
        )
        .filter(GameReview.created_at >= thirty_days_ago)
        .group_by("date")
        .order_by("date")
        .all()
    )

    return [StatPointOut(label=str(row[0]), value=row[1]) for row in results]

@router.get("/top-games", response_model=List[TopItemOut])
async def get_top_games(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # returns games with the most reviews
    results = (
        db.query(
            Game.id,
            Game.title,
            func.count(GameReview.id).label("review_count")
        )
        .join(GameReview, Game.id == GameReview.game_id)
        .group_by(Game.id)
        .order_by(func.count(GameReview.id).desc())
        .limit(limit)
        .all()
    )

    return [TopItemOut(id=row[0], title=row[1], count=row[2]) for row in results]

# admin stats

@router.get("/admin/users-growth", response_model=List[StatPointOut], dependencies=[Depends(require_admin)])
async def get_users_growth(
    db: Session = Depends(get_db)
):
    #returns number of new users per day for the last 15 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=15)

    results = (
        db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count")
        )
        .filter(User.created_at >= thirty_days_ago)
        .group_by("date")
        .order_by("date")
        .all()
    )

    return [StatPointOut(label=str(row[0]), value=row[1]) for row in results]

@router.get("/admin/revenue", response_model=List[StatValueOut], dependencies=[Depends(require_admin)])
async def get_revenue_stats(
    db: Session = Depends(get_db)
):
    #returns total revenue
    thirty_days_ago = datetime.utcnow() - timedelta(days=15)

    results = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total).label("total")
        )
        .filter(Order.created_at >= thirty_days_ago)
        .group_by("date")
        .order_by("date")
        .all()
    )

    return [StatValueOut(label=str(row[0]), value=float(row[1] or 0)) for row in results]

@router.get("/admin/orders-count", response_model=List[StatPointOut], dependencies=[Depends(require_admin)])
async def get_orders_count(
    db: Session = Depends(get_db)
):
    #returns number of orders
    thirty_days_ago = datetime.utcnow() - timedelta(days=15)

    results = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("count")
        )
        .filter(Order.created_at >= thirty_days_ago)
        .group_by("date")
        .order_by("date")
        .all()
    )

    return [StatPointOut(label=str(row[0]), value=row[1]) for row in results]