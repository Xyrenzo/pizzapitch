from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

IMAGES_DIR = STATIC_DIR / "img"