from fastapi import FastAPI
from app.api.routes import router
from app.config import APP_NAME, APP_VERSION

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "PDF Summarizer API", "version": APP_VERSION}
