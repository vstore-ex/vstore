import re
import uuid
import httpx
from app.services.media import media_service


class MarkdownService:
    def __init__(self):
        self.img_pattern = re.compile(r'!\[(.*?)\]\((https?://[^\s)]+)\)')

    async def process_content(self, text: str, allow_images: bool = True) -> str:
        if not text:
            return ""

        if not allow_images:
            return self.img_pattern.sub("", text)

        async with httpx.AsyncClient(timeout=10.0) as client:
            matches = list(self.img_pattern.finditer(text))
            for match in matches:
                alt_text = match.group(1)
                img_url = match.group(2)

                if "blob.core.windows.net" in img_url:
                    continue

                try:
                    res = await client.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        webp_bytes = media_service.convert_to_webp(res.content)
                        filename = f"md_{uuid.uuid4()}.webp"
                        azure_url = media_service.upload_bytes(
                            webp_bytes, 
                            filename, 
                            content_type="image/webp"
                        )
                        
                        old_tag = match.group(0)
                        new_tag = f"![{alt_text}]({azure_url})"
                        text = text.replace(old_tag, new_tag)
                except Exception as e:
                    continue

        return text


markdown_service = MarkdownService()