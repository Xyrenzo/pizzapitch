from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"
TEMPLATES_DIR = BASE_DIR / "templates"