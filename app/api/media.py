from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.media import media_service
import uuid
import os

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="This file is not an image")

    try:
        file_bytes = await file.read()

        # convert to webp
        webp_bytes = media_service.convert_to_webp(file_bytes)

        # generate unique filename
        ext = ".webp"
        filename = f"{uuid.uuid4()}{ext}"

        # azure
        url = media_service.upload_to_azure(webp_bytes, filename)

        return {"url": url, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")