from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Game, Artwork
from app.models.comment import CommentThread
from app.schemas import ArtworkCreate, ArtworkUpdate, ArtworkOut
from app.api.auth.authorization import get_current_user, require_admin
from app.services.markdown import markdown_service
from app.models.user import User

router = APIRouter(prefix="/artworks", tags=["artworks"])

@router.get("/", response_model=List[ArtworkOut])
async def list_artworks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    artworks = db.query(Artwork).offset(skip).limit(limit).all()

    result = []
    for a in artworks:
        data = a.__dict__.copy()
        data["username"] = a.author.username
        result.append(ArtworkOut(**data))
    return result

@router.get("/game/{game_id}", response_model=List[ArtworkOut])
async def list_game_artworks(game_id: int, db: Session = Depends(get_db)):
    artworks = db.query(Artwork).filter(Artwork.game_id == game_id).all()

    result = []
    for a in artworks:
        data = a.__dict__.copy()
        data["username"] = a.author.username
        result.append(ArtworkOut(**data))
    return result

@router.get("/{artwork_id}", response_model=ArtworkOut)
async def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="artwork not found")

    data = artwork.__dict__.copy()
    data["username"] = artwork.author.username
    return ArtworkOut(**data)

@router.post("/", response_model=ArtworkOut, status_code=status.HTTP_201_CREATED)
async def create_artwork(
    artwork_in: ArtworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # validate game exists
    game = db.query(Game).filter(Game.id == artwork_in.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    # artworks must have a comment thread
    thread = CommentThread()
    db.add(thread)
    db.flush()

    # no images
    processed_md = await markdown_service.process_content(
        artwork_in.description_md,
        allow_images=False
    ) if artwork_in.description_md else None

    artwork = Artwork(
        game_id=artwork_in.game_id,
        author_id=current_user.id,
        thread_id=thread.id,
        title=artwork_in.title,
        image_url=artwork_in.image_url,
        description_md=processed_md
    )
    db.add(artwork)
    db.commit()
    db.refresh(artwork)

    data = artwork.__dict__.copy()
    data["username"] = current_user.username
    return ArtworkOut(**data)

@router.put("/{artwork_id}", response_model=ArtworkOut)
async def update_artwork(
    artwork_id: int,
    artwork_in: ArtworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="artwork not found")

    if artwork.author_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")

    if artwork_in.description_md is not None:
        artwork.description_md = await markdown_service.process_content(
            artwork_in.description_md,
            allow_images=False
        )

    if artwork_in.title is not None:
        artwork.title = artwork_in.title

    if artwork_in.image_url is not None:
        artwork.image_url = artwork_in.image_url

    db.commit()
    db.refresh(artwork)

    data = artwork.__dict__.copy()
    data["username"] = artwork.author.username
    return ArtworkOut(**data)

@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artwork(
    artwork_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="artwork not found")

    if artwork.author_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="not allowed")

    db.delete(artwork)
    db.commit()
    return None