from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.api.auth.authorization import require_admin
from app.models import DiscoverLayout, Game
from app.schemas import (
    DiscoverLayoutOut,
    DiscoverLayoutUpdate,
    DiscoverSectionOut,
    DiscoverPromoOut,
    DiscoverRankedColumnOut,
    GameListOut
)

router = APIRouter(prefix="/discover", tags=["discover"])

@router.get("/discover", response_model=DiscoverLayoutOut)
async def get_discover_page(db: Session = Depends(get_db)):
    layout = db.query(DiscoverLayout).filter(DiscoverLayout.id == 1).first()

    if not layout:
        return DiscoverLayoutOut()

    # collect all game ids to fetch in one batch
    game_ids = set()
    if layout.featured_game_id:
        game_ids.add(layout.featured_game_id)

    for section in layout.sections or []:
        game_ids.update(section.get("game_ids", []))

    game_ids.update(layout.deals_game_ids or [])
    game_ids.update(layout.free_games_game_ids or [])

    for col in layout.ranked_columns or []:
        game_ids.update(col.get("game_ids", []))

    # batch fetch games
    games_map = {
        g.id: GameListOut.model_validate(g)
        for g in db.query(Game).filter(Game.id.in_(list(game_ids))).all()
    }

    # layout
    return DiscoverLayoutOut(
        featured=games_map.get(layout.featured_game_id) if layout.featured_game_id else None,
        sections=[
            DiscoverSectionOut(
                id=s.get("id"),
                title=s.get("title"),
                games=[games_map[gid] for gid in s.get("game_ids", []) if gid in games_map]
            ) for s in layout.sections or []
        ],
        promos=layout.promos or [],
        deals=[games_map[gid] for gid in layout.deals_game_ids or [] if gid in games_map],
        free_games=[games_map[gid] for gid in layout.free_games_game_ids or [] if gid in games_map],
        ranked_columns=[
            DiscoverRankedColumnOut(
                title=c.get("title"),
                games=[games_map[gid] for gid in c.get("game_ids", []) if gid in games_map]
            ) for c in layout.ranked_columns or []
        ],
        mobile_banner=layout.mobile_banner
    )

@router.patch("/admin/discover")
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
    return {"message": "Updated successfully"}