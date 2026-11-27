
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_NAME = os.getenv("STOCKLINE_MODEL", "gemini-3.6-flash")

APP_NAME = "stockline"

# Keep persistent sessions in a dedicated, writable user directory.
DATA_DIR = Path.home() / ".stockline"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    "STOCKLINE_DATABASE_URL",
    f"sqlite+aiosqlite:///{DATA_DIR / 'stockline_sessions.db'}",
)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "STOCKLINE_CORS_ORIGINS",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]
