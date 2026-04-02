import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "traffic_data.db"

# Model configuration
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")

CONGESTION_THRESHOLDS = {
    "LOW": 8,
    "MEDIUM": 15
}

# Inference & Processing Hardware
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# UI Streaming Optimization
UI_POLLING_INTERVAL_MS = 50  # 20 FPS refresh rate for smooth video

# Tracking and Analytics
PIXELS_PER_METER = 8.0  # Recalibrated for realistic 40-80 km/h highway scale
LANE_COORD_X = [426, 853]  # Deprecated - using perspective model

# Perspective Lane Geometry (Trapezoidal Model)
# Points structured as: [Lane0_L, Lane1_L, Lane2_L, Lane3_L, Lane4_R]
LANE_TOP_Y = 350
LANE_BOTTOM_Y = 720
LANE_TOP_X = [580, 610, 640, 670, 700]
LANE_BOTTOM_X = [100, 370, 640, 910, 1180]

HISTORY_LIMIT = 50
PREDICTION_WINDOW = 20  # Number of data points for moving average
TRAFFIC_FLOW_WINDOW = 60  # Seconds to calculate vehicles per minute
