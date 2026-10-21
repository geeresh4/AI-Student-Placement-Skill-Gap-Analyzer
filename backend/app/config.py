import os
from pathlib import Path
from dotenv import load_dotenv
BASE = Path(__file__).resolve().parents[2]
load_dotenv(BASE / ".env")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE / 'backend' / 'placement.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "local-demo-only-change-before-deploy")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE / "models" / "placement_model.joblib")))
if not MODEL_PATH.is_absolute(): MODEL_PATH = BASE / MODEL_PATH
