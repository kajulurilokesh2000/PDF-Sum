from PyPDF2 import PdfReader
from fastapi import UploadFile
import os

async def extract_text_from_pdf(file: UploadFile, upload_dir: str) -> str:
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    os.remove(file_path)
    return text.strip()
