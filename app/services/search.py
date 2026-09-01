from typing import Optional, List, Type, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from azure.storage.blob import BlobServiceClient
from app.services.media import media_service


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

    def get_blob_content(self, blob_name: str, container: str = "media") -> Optional[str]:
        try:
            return media_service.read_text_blob(blob_name, container=container)
        except Exception:
            return None

    def search_all_markdowns(self, query: str, container: str = "media") -> List[dict]:
        """
        Scans all .md files in the container and returns matches for the given query.
        """
        if not query:
            return []

        results = []
        try:
            blob_service_client = BlobServiceClient.from_connection_string(media_service.connection_string)
            container_client = blob_service_client.get_container_client(container)
            
            for blob in container_client.list_blobs():
                if blob.name.endswith(".md"):
                    content = self.get_blob_content(blob.name, container=container)
                    if content and query.lower() in content.lower():
                        matches = [line for line in content.splitlines() if query.lower() in line.lower()]
                        results.append({
                            "blob_name": blob.name,
                            "matches": matches
                        })
        except Exception:
            pass

        return results

search_service = SearchService()