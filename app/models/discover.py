from sqlalchemy import Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List
from app.models.base import Base

class DiscoverLayout(Base):
    __tablename__ = "discover_layout"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    featured_game_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("games.id"), nullable=True)

    # json columns
    sections: Mapped[list] = mapped_column(JSON, default=list)
    promos: Mapped[list] = mapped_column(JSON, default=list)
    deals_game_ids: Mapped[list] = mapped_column(JSON, default=list)
    free_games_game_ids: Mapped[list] = mapped_column(JSON, default=list)
    ranked_columns: Mapped[list] = mapped_column(JSON, default=list)
    mobile_banner: Mapped[dict] = mapped_column(JSON, default=dict)