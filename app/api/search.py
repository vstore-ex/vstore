from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import User, Game, GameReview
from app.services.search import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/users")
async def search_users(q: str = Query("", description="search term"), db: Session = Depends(get_db)):
    users = search_service.search_model(
        db=db,
        model=User,
        search_fields=[User.username, User.full_name, User.email],
        query=q
    )

    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "role_name": u.role.name
        }
        for u in users
    ]


@router.get("/games")
async def search_games(q: str = Query("", description="search by title, description, developer or publisher"), db: Session = Depends(get_db)):
    games = search_service.search_model(
        db=db,
        model=Game,
        search_fields=[Game.title, Game.description_md, Game.developer, Game.publisher],
        query=q
    )
    return games


@router.get("/reviews")
async def search_reviews(q: str = Query("", description="search inside review text"), db: Session = Depends(get_db)):
    reviews = search_service.search_model(
        db=db,
        model=GameReview,
        search_fields=[GameReview.content_md],
        query=q
    )
    return reviews