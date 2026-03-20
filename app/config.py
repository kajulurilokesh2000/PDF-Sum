from dotenv import load_dotenv
import os

load_dotenv()

AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_BASE = os.getenv("AZURE_API_BASE")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
APP_NAME = os.getenv("APP_NAME", "PDF Summarizer API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", 2000))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
