from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.core.config import settings
import os
import uuid
import shutil

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Validate size (simple check if possible, or read and check)
    # UploadFile might not have size easily until read, but we can check after read or rely on middleware if configured
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    uploads_path = os.path.join(os.getcwd(), settings.UPLOAD_DIR)
    
    if not os.path.exists(uploads_path):
        os.makedirs(uploads_path)

    filepath = os.path.join(uploads_path, unique_filename)
    
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    finally:
        file.file.close()

    # Return the URL for the frontend to use
    # We return the absolute URL from the point of view of the root/domain
    file_url = f"{settings.MEDIA_URL}/{unique_filename}"
    
    return {
        "url": file_url,
        "filename": unique_filename
    }
