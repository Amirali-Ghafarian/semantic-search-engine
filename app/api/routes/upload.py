import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.schemas.document import UploadedDocumentSummary
from app.services.search_service import SearchService, get_search_service

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadedDocumentSummary, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    search_service: SearchService = Depends(get_search_service),
) -> UploadedDocumentSummary:
    try:
        filename = Path(file.filename or "uploaded.pdf").name
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported.",
            )

        settings = get_settings()
        stored_path = settings.raw_data_dir / f"{uuid4().hex}_{filename}"

        with stored_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return search_service.ingest_document(stored_path, original_filename=filename)
    except ValueError as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        await file.close()