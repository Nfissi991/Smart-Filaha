# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME    = "Plant Disease Detector"
APP_VERSION = "v3.0"
APP_ICON    = "🌿"

# ── Couleurs (tbqaw kif hiaw — ma tbdlhomch) ──
COLORS = {
    "primary_dark":   "#1C3A2F",
    "primary_mid":    "#2D5240",
    "primary_light":  "#253D30",
    "accent_green":   "#A8D5B5",
    "accent_beige":   "#E8DFC8",
    "bg_page":        "#F5F0E8",
    "bg_card":        "#FDFAF4",
    "bg_input":       "#F0EBE0",
    "border":         "#DDD5C0",
    "border_dashed":  "#C4B89A",
    "text_dark":      "#1C3A2F",
    "text_mid":       "#7A6E5C",
    "text_muted":     "#9A8E7C",
    "bar_high":       "#C0392B",
    "bar_med":        "#C49A00",
    "bar_low":        "#5A8A6A",
    "bar_none":       "#1D9E75",
    "bar_confidence": "#2D5240",
}

# ── Langues supportées ──
LANGUAGES = ["دارجة", "العربية", "Français", "English"]

# ── DB ──
DB_URL = os.getenv("DATABASE_URL", "sqlite:///plant_detector.db")
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# ── Modèle ──
MODEL_PATH      = "archive_best_model.h5"
CLASS_NAMES_PATH = "class_names.json"
IMG_SIZE        = (128, 128)

# ── Auth ──
SECRET_KEY      = "change_this_in_production"
SESSION_TIMEOUT = 3600  # secondes

# ── Upload ──
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_HISTORY        = 15

UPLOAD_ROOT = "storage/uploads"
PRODUCT_UPLOAD_DIR = f"{UPLOAD_ROOT}/products"
PUBLICATION_UPLOAD_DIR = f"{UPLOAD_ROOT}/publications"
MAX_UPLOAD_SIZE_MB = 5