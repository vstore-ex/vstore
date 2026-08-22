import io
from PIL import Image
from azure.storage.blob import BlobServiceClient
from app.core.config import settings

class MediaService:
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = "media"

    def convert_to_webp(self, file_bytes: bytes) -> bytes:
        with Image.open(io.BytesIO(file_bytes)) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            output = io.BytesIO()
            img.save(output, format="WEBP", quality=75)
            return output.getvalue()

    def upload_to_azure(self, file_bytes: bytes, filename: str) -> str:
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=filename)

        blob_client.upload_blob(file_bytes, overwrite=True)

        return blob_client.url

media_service = MediaService()