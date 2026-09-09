from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.api.auth.authorization import require_admin
from app.models.game import Game
from app.models.taxonomy import Tag
from app.schemas import (
    TagCreate, TagOut,
    GameCreate, GameOut, GameAdminUpdate
)

router = APIRouter(prefix="/admin", tags=["admin"])

# tags

@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    slug = tag_in.name.lower().replace(" ", "-")

    existing = db.query(Tag).filter((Tag.name == tag_in.name) | (Tag.slug == slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="tag with this name or slug already exists")

    tag = Tag(name=tag_in.name, slug=slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.patch("/tags/{tag_id}", response_model=TagOut)
async def update_tag(
    tag_id: int,
    tag_in: TagCreate, # reuse TagCreate for simplicity
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="tag not found")

    slug = tag_in.name.lower().replace(" ", "-")

    conflict = db.query(Tag).filter(
        (Tag.id != tag_id) & ((Tag.name == tag_in.name) | (Tag.slug == slug))
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="another tag already has this name or slug")

    tag.name = tag_in.name
    tag.slug = slug
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="tag not found")

    db.delete(tag)
    db.commit()
    return None

# games

@router.post("/games", response_model=GameOut, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_in: GameCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    tags = []
    if game_in.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(game_in.tag_ids)).all()
        if len(tags) != len(game_in.tag_ids):
            raise HTTPException(status_code=400, detail="one or more tag id are invalid")

    game_data = game_in.model_dump(exclude={"tag_ids"})
    game = Game(**game_data, tags=tags)

    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@router.patch("/games/{game_id}", response_model=GameOut)
async def update_game(
    game_id: int,
    game_in: GameAdminUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    update_data = game_in.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    for key, value in update_data.items():
        setattr(game, key, value)

    if tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        if len(tags) != len(tag_ids):
            raise HTTPException(status_code=400, detail="one or more tag IDs are invalid")
        game.tags = tags

    db.commit()
    db.refresh(game)
    return game

@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_game(
    game_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    game.is_active = False
    db.commit()
    return None