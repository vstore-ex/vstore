import io
import os
import tempfile
import uuid
from PIL import Image
from azure.storage.blob import BlobServiceClient, ContentSettings
from app.core.config import settings
import ffmpeg

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

    def upload_bytes(self, file_bytes: bytes, filename: str, content_type: str = "image/webp") -> str:
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=filename)

        blob_client.upload_blob(
            file_bytes,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type)
        )
        return blob_client.url

    def delete_blob(self, filename: str) -> bool:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=filename)
            blob_client.delete_blob()
            return True
        except Exception:
            return False

    def process_video(self, file_bytes: bytes, filename: str) -> tuple[str, str]:
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, f"input_{uuid.uuid4()}.mp4")
        thumb_path = os.path.join(temp_dir, f"thumb_{uuid.uuid4()}.jpg")

        try:
            # save to temp file
            with open(video_path, "wb") as f:
                f.write(file_bytes)

            # extract thumbnail using ffmpeg
            (
                ffmpeg
                .input(video_path, ss=1)
                .filter('scale', 480, -1)
                .output(thumb_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            # convert thumbnail to webp
            with open(thumb_path, "rb") as f:
                webp_bytes = self.convert_to_webp(f.read())

            thumb_filename = filename.rsplit('.', 1)[0] + ".webp"

            # upload video
            video_url = self.upload_bytes(file_bytes, filename, content_type="video/mp4")

            # upload thumbnail
            thumb_url = self.upload_bytes(webp_bytes, thumb_filename)

            return video_url, thumb_url

        finally:
            # clean temp files
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)

media_service = MediaService()