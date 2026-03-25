from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from typing import Dict

from app.services.pdf_service import extract_text_from_pdf
from app.services.summary_service import summarize_text
from app.config import UPLOAD_DIR

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)) -> Dict[str, str]:
    filename = file.filename or ""
    content_type = (file.content_type or "").lower()
    if not (filename.lower().endswith(".pdf") or content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        extracted_text = await extract_text_from_pdf(file, UPLOAD_DIR)
        summary_text = summarize_text(extracted_text)
        return {"filename": filename, "summary": summary_text}
    except Exception:
        logger.exception("Failed to summarize PDF: %s", filename)
        raise HTTPException(status_code=500, detail="Failed to summarize PDF")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}