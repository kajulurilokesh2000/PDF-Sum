from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import extract_text_from_pdf
from app.services.summary_service import summarize_text
from app.config import UPLOAD_DIR

router = APIRouter()

@router.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        text = await extract_text_from_pdf(file, UPLOAD_DIR)
        summary = summarize_text(text)
        return {"filename": file.filename, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
