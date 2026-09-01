import re
import uuid
import urllib.request
from app.services.media import media_service

class MarkdownService:
    def __init__(self):
        self.img_pattern = re.compile(r'!\[(.*?)\]\((https?://[^\s)]+)\)')

    def process_and_upload(self, markdown_text: str, filename: str) -> str:
        def replace_match(match):
            alt_text = match.group(1)
            img_url = match.group(2)

            if "blob.core.windows.net" in img_url:
                return match.group(0)

            try:
                req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    img_bytes = response.read()

                webp_bytes = media_service.convert_to_webp(img_bytes)
                new_filename = f"{uuid.uuid4()}.webp"
                azure_url = media_service.upload_bytes(webp_bytes, new_filename, content_type="image/webp")

                return f"![{alt_text}]({azure_url})"
            except Exception:
                return match.group(0)

        processed_content = self.img_pattern.sub(replace_match, markdown_text)
        return media_service.upload_bytes(
            processed_content.encode("utf-8"),
            filename,
            content_type="text/markdown"
        )

    def read_markdown(self, filename: str) -> str:
        return media_service.read_text_blob(filename)

    # useless for prod method
    def create_markdown_from_text(self, text_content: str) -> dict:
        filename = f"test_{uuid.uuid4()}.md"
        url = self.process_and_upload(text_content, filename)
        return {
            "url": url,
            "filename": filename,
            "original_text": text_content
        }

markdown_service = MarkdownService()