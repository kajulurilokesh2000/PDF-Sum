from PyPDF2 import PdfReader
from fastapi import UploadFile
import io

async def extract_text_from_pdf(upload_file: UploadFile) -> str:
    """Extract text from an uploaded PDF without writing it to disk."""
    data = await upload_file.read()
    if not data:
        return ""
    buffer = io.BytesIO(data)
    reader = PdfReader(buffer)
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text).strip()