import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash-lite"


CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCUMENT_DIR = os.path.join(BASE_DIR, "documents")