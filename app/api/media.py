from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.media import media_service
import uuid
from app.api.auth.authorization import require_admin

router = APIRouter(tags=["media"])

@router.post("/media/upload")
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

@router.post("/admin/uploads", status_code=201)
async def admin_upload_image(
    file: UploadFile = File(...),
    admin=Depends(require_admin)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="not an image")

    try:
        file_bytes = await file.read()
        webp_bytes = media_service.convert_to_webp(file_bytes)
        filename = f"admin_{uuid.uuid4()}.webp"
        url = media_service.upload_bytes(webp_bytes, filename, content_type="image/webp")

        return {"url": url, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"upload failed: {str(e)}")

@router.delete("/admin/uploads/{blob_name}", status_code=204)
async def delete_blob(
    blob_name: str,
    admin=Depends(require_admin)
):
    if media_service.delete_blob(blob_name):
        return None
    raise HTTPException(status_code=404, detail="not found")