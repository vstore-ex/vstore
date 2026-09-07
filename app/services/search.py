from typing import List, Type, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_


class SearchService:
    def search_model(
        self,
        db: Session,
        model: Type[Any],
        search_fields: List[Any],
        query: str,
        limit: int = 20
    ) -> List[Any]:
        if not query or not search_fields:
            return []

        search_filter = f"%{query}%"
        filters = [field.ilike(search_filter) for field in search_fields]

        return (
            db.query(model)
            .filter(or_(*filters))
            .limit(limit)
            .all()
        )


search_service = SearchService()