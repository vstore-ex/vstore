from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.media import media_service
import uuid

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="not an image")

    try:
        file_bytes = await file.read()
        webp_bytes = media_service.convert_to_webp(file_bytes)
        filename = f"{uuid.uuid4()}.webp"
        url = media_service.upload_bytes(webp_bytes, filename, content_type="image/webp")

        return {"url": url, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"upload failed: {str(e)}")