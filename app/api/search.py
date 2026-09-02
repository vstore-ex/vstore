from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import User
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

@router.get("/markdown")
async def search_markdown(
    q: str = Query(..., description="query string to search across all stored markdown files"),
    container: str = "media"
):
    return search_service.search_all_markdowns(query=q, container=container)