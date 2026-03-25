from dotenv import load_dotenv
from os import environ
from pathlib import Path

load_dotenv()

def _env(key, default=None):
    val = environ.get(key)
    return val if val is not None else default

def _env_int(key, default):
    val = environ.get(key)
    try:
        return int(val) if val is not None else default
    except (TypeError, ValueError):
        return default

AZURE_API_KEY = _env("AZURE_API_KEY")
AZURE_API_BASE = _env("AZURE_API_BASE")
AZURE_API_VERSION = _env("AZURE_API_VERSION")
AZURE_DEPLOYMENT_NAME = _env("AZURE_DEPLOYMENT_NAME")

APP_NAME = _env("APP_NAME", "PDF Summarizer API")
APP_VERSION = _env("APP_VERSION", "1.0.0")

MAX_CHUNK_SIZE = _env_int("MAX_CHUNK_SIZE", 2000)
UPLOAD_DIR = Path(_env("UPLOAD_DIR", "uploads")).resolve()

__all__ = [
    "AZURE_API_KEY",
    "AZURE_API_BASE",
    "AZURE_API_VERSION",
    "AZURE_DEPLOYMENT_NAME",
    "APP_NAME",
    "APP_VERSION",
    "MAX_CHUNK_SIZE",
    "UPLOAD_DIR",
]