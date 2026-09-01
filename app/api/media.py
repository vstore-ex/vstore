from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.media import media_service
from app.services.markdown import markdown_service
import uuid

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="This file is not an image")

    try:
        file_bytes = await file.read()
        webp_bytes = media_service.convert_to_webp(file_bytes)
        filename = f"{uuid.uuid4()}.webp"
        url = media_service.upload_bytes(webp_bytes, filename, content_type="image/webp")

        return {"url": url, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload-markdown")
async def upload_markdown(file: UploadFile = File(...)):
    if not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="This file is not a markdown file")

    try:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8")

        filename = f"{uuid.uuid4()}.md"
        url = markdown_service.process_and_upload(content_str, filename)

        return {"url": url, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdown upload failed: {str(e)}")

# for more comfortable test
@router.post("/test-create-markdown")
async def test_create_markdown(text: str):
    try:
        return markdown_service.create_markdown_from_text(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test creation failed: {str(e)}")