from fastapi import FastAPI
from app.api.routes import router as api_router
from app.config import APP_NAME, APP_VERSION

API_PREFIX = "/api"

app = FastAPI(title=APP_NAME, version=APP_VERSION, description="PDF Summarizer API")

app.include_router(api_router, prefix=API_PREFIX)


@app.get("/", summary="Service root")
def root() -> dict:
    """Return basic service information."""
    return {"message": app.title, "version": app.version}