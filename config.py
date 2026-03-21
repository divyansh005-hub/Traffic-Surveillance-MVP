import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "traffic_data.db"

# Model configuration
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")

CONGESTION_THRESHOLDS = {
    "LOW": 8,
    "MEDIUM": 15
}
