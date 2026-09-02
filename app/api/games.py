from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.models import Game, Genre, Tag, User
from app.schemas import GameCreate, GameUpdate, GameOut, GameListOut
from app.api.auth.authorization import get_current_user, require_admin

router = APIRouter(prefix="/games", tags=["games"])

# public

@router.get("/", response_model=List[GameListOut])
async def list_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    genre_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Game).options(
        joinedload(Game.genres),
        joinedload(Game.tags),
        joinedload(Game.banners)
    )

    if genre_id:
        query = query.filter(Game.genres.any(Genre.id == genre_id))
    if tag_id:
        query = query.filter(Game.tags.any(Tag.id == tag_id))

    return query.offset(skip).limit(limit).all()

@router.get("/{game_id}", response_model=GameOut)
async def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).options(
        joinedload(Game.genres),
        joinedload(Game.tags),
        joinedload(Game.banners),
        joinedload(Game.media)
    ).filter(Game.id == game_id).first()

    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    return game

# admin

@router.post("/", response_model=GameOut, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_in: GameCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    game_data = game_in.model_dump(exclude={"genre_ids", "tag_ids"})
    game = Game(**game_data)

    if game_in.genre_ids:
        game.genres = db.query(Genre).filter(Genre.id.in_(game_in.genre_ids)).all()
    if game_in.tag_ids:
        game.tags = db.query(Tag).filter(Tag.id.in_(game_in.tag_ids)).all()

    db.add(game)
    db.commit()
    db.refresh(game)

    return game

@router.put("/{game_id}", response_model=GameOut)
async def update_game(
    game_id: int,
    game_in: GameUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    update_data = game_in.model_dump(exclude_unset=True)

    if "genre_ids" in update_data:
        genre_ids = update_data.pop("genre_ids")
        if genre_ids is not None:
            game.genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()

    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            game.tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()

    for field, value in update_data.items():
        setattr(game, field, value)

    db.commit()
    db.refresh(game)

    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    db.delete(game)
    db.commit()

    return None