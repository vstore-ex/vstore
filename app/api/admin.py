from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.db import get_db
from app.api.auth.authorization import require_admin
from app.models.game import Game, GameBanner, GameMedia, BannerType, MediaType
from app.models.taxonomy import Tag
from app.models.achievement import Achievement
from app.models.discover import DiscoverLayout
from app.models.review import GameReview
from app.models.order import Order
from app.models.user import User, Role
from app.schemas import (
    TagCreate, TagOut,
    GameCreate, GameOut, GameAdminUpdate,
    AchievementCreate, AchievementOut,
    GameBannerOut, GameMediaOut,
    UserUpdate, UserAdminUpdate, UserOut,
    DiscoverLayoutUpdate
)
from app.services.media import media_service

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

# media n banners

@router.post("/games/{game_id}/banners", response_model=GameBannerOut)
async def upload_game_banner(
    game_id: int,
    banner_type: BannerType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="file must be an image")

    try:
        file_bytes = await file.read()
        webp_bytes = media_service.convert_to_webp(file_bytes)
        filename = f"banners/{game_id}_{banner_type}.webp"
        url = media_service.upload_bytes(webp_bytes, filename)

        # check for existing banner of this type and update it, or create new
        banner = db.query(GameBanner).filter(
            GameBanner.game_id == game_id,
            GameBanner.banner_type == banner_type
        ).first()

        if banner:
            banner.image_url = url
        else:
            banner = GameBanner(game_id=game_id, banner_type=banner_type, image_url=url)
            db.add(banner)

        db.commit()
        db.refresh(banner)
        return banner
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"banner upload failed: {str(e)}")

@router.post("/games/{game_id}/media", response_model=GameMediaOut)
async def upload_game_media(
    game_id: int,
    media_type: MediaType = Form(...),
    sort_order: int = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    try:
        file_bytes = await file.read()
        thumbnail_url = None

        if media_type == MediaType.IMAGE:
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="file must be an image")
            webp_bytes = media_service.convert_to_webp(file_bytes)
            filename = f"gallery/{game_id}_{uuid.uuid4()}.webp"
            url = media_service.upload_bytes(webp_bytes, filename)
        elif media_type == MediaType.VIDEO:
            # use the new process_video method
            filename = f"gallery/{game_id}_{uuid.uuid4()}_{file.filename}"
            url, thumbnail_url = media_service.process_video(file_bytes, filename)
        else:
            raise HTTPException(status_code=400, detail="invalid media type")

        media = GameMedia(
            game_id=game_id,
            media_type=media_type,
            url=url,
            thumbnail_url=thumbnail_url,
            sort_order=sort_order
        )
        db.add(media)
        db.commit()
        db.refresh(media)
        return media
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"media upload failed: {str(e)}")

# achievements

@router.post("/games/{game_id}/achievements", response_model=AchievementOut, status_code=status.HTTP_201_CREATED)
async def create_game_achievement(
    game_id: int,
    achievement_in: AchievementCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="game not found")

    # id is required in AchievementCreate based on schemas.py
    existing = db.query(Achievement).filter(Achievement.id == achievement_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="achievement with this ID already exists")

    achievement = Achievement(
        id=achievement_in.id,
        product_id=game_id,
        title=achievement_in.title,
        description=achievement_in.description,
        icon=achievement_in.icon,
        completion_percent=achievement_in.completion_percent
    )
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement

# discover

@router.patch("/discover", status_code=status.HTTP_200_OK)
async def update_discover_layout(
    update_data: DiscoverLayoutUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    layout = db.query(DiscoverLayout).filter(DiscoverLayout.id == 1).first()

    if not layout:
        layout = DiscoverLayout(id=1)
        db.add(layout)

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(layout, key, value)

    db.commit()
    db.refresh(layout)
    return {"message": "updated successfully"}

# moderation and management

@router.patch("/reviews/{review_id}/hide", status_code=status.HTTP_200_OK)
async def toggle_review_visibility(
    review_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    review = db.query(GameReview).filter(GameReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="review not found")

    review.is_hidden = not review.is_hidden
    db.commit()
    return {"message": f"Review {'hidden' if review.is_hidden else 'visible'}"}

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review_admin(
    review_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    review = db.query(GameReview).filter(GameReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="review not found")

    db.delete(review)
    db.commit()
    return None

@router.patch("/orders/{order_id}", status_code=status.HTTP_200_OK)
async def update_order_status(
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")

    order.status = status
    db.commit()
    return {"message": f"Order status updated to {status}"}

@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user_admin(
    user_id: int,
    user_in: UserAdminUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    update_data = user_in.model_dump(exclude_unset=True)
    role_id = update_data.pop("role_id", None)

    for key, value in update_data.items():
        setattr(user, key, value)

    if role_id is not None:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="invalid role id")
        user.role_id = role.id

    db.commit()
    db.refresh(user)

    from app.api.users import get_user_stats, build_user_out
    stats = get_user_stats(db, user.id)
    return build_user_out(user, stats)