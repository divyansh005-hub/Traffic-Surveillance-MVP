# 🚦 Smart Traffic Intelligence Platform (STCS)

> **ET 201 — IoT-Based Traffic Surveillance System**
> A real-time, AI-powered traffic monitoring and analytics platform built with YOLO11, FastAPI, and a cyberpunk-style live dashboard.

![Status](https://img.shields.io/badge/status-live-brightgreen)
![YOLO](https://img.shields.io/badge/AI-YOLO11-blue)
![Python](https://img.shields.io/badge/python-3.12-yellow)
![GPU](https://img.shields.io/badge/hardware-NVIDIA%20CUDA-76b900)

---

## 📸 System Overview

The Smart Traffic Control System (STCS) is a fully integrated, production-grade traffic surveillance pipeline that processes live highway camera feeds to:

- Detect and track vehicles in real-time using **YOLO11** (Ultralytics)
- Assign vehicles to **perspective-aware lanes** using a trapezoidal road model
- Estimate **realistic vehicle speeds** (40–80 km/h range) via calibrated pixel-to-meter scaling
- Serve live metrics via a **FastAPI REST backend**
- Visualize everything on a **cyberpunk glassmorphism dashboard** with neon motion trails, glowing bounding boxes, and a real-time HUD

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  run_all.bat (Launcher)                 │
├──────────────┬───────────────────────┬──────────────────┤
│  FastAPI     │   YOLO11 Inference    │  HTTP File Server │
│  Backend     │   Engine (GPU/CPU)    │  Frontend :8080  │
│  :8001       │   ml/inference.py     │  frontend/       │
└──────────────┴───────────────────────┴──────────────────┘
       ↑                   ↓
  REST API            data/*.json / *.txt
  /metrics            (atomic safe-replace)
  /results
```

**Data Flow:**
1. `run_all.bat` starts Backend → Frontend → Inference Engine
2. `ml/inference.py` reads the video source frame-by-frame, runs YOLO11 tracking
3. Metrics + encoded frames are written atomically to `data/`
4. Frontend (`app.js`) polls the backend every **50ms** for smooth ~20 FPS display

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- NVIDIA GPU with CUDA 12.1+ (highly recommended for 30+ FPS)
- Windows (for `run_all.bat`)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**For NVIDIA GPU acceleration (strongly recommended):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
```

### 2. Add Your Video Source

Place your traffic camera video in the `data/` folder. Update `run_all.bat` if your filename differs:
```bat
set VIDEO_SOURCE=data\BackVehcilesTraffic720p.mp4
```

### 3. Launch the Full System

```bat
run_all.bat
```

This single command starts all three services:
- **Backend API** → `http://localhost:8001`
- **Frontend Dashboard** → `http://localhost:8080`
- **YOLO11 Inference Engine** (GPU accelerated)

> First run will automatically download the `yolo11n.pt` model weights (~6MB).

---

## 📁 Project Structure

```
traffic-surveillance-mvp/
├── run_all.bat              # 🚀 One-click launcher (Windows)
├── run_all.py               # Python launcher alternative
├── config.py                # Central configuration (model, GPU, lanes, thresholds)
│
├── backend/
│   ├── main.py              # FastAPI REST API endpoints
│   └── database.py          # SQLAlchemy SQLite ORM models
│
├── ml/
│   ├── inference.py         # Core YOLO11 processing loop (GPU-accelerated)
│   ├── lane.py              # Perspective-aware lane detection engine
│   ├── speed.py             # Speed estimation (pixels → km/h)
│   ├── tracking.py          # Vehicle history & state management
│   ├── metrics.py           # Flow rate & density calculations
│   ├── prediction.py        # Traffic count prediction & trend analysis
│   └── performance.py       # FPS & latency monitoring
│
├── frontend/
│   ├── index.html           # Cyberpunk dashboard UI (Tailwind CSS)
│   ├── app.js               # Real-time polling & chart rendering
│   └── style.css            # Glassmorphism custom styles
│
├── scripts/
│   ├── run_inference.py     # CLI script for manual inference runs
│   ├── run_server.py        # Standalone backend server launcher
│   └── migrate_db.py        # Database migration helper
│
├── data/                    # Video sources & live data files (gitignored)
│   ├── latest_frame.txt     # Base64-encoded current frame
│   └── latest_metrics.json  # Latest JSON metrics for dashboard
│
└── requirements.txt
```

---

## ⚙️ Configuration (`config.py`)

| Parameter | Default | Description |
|---|---|---|
| `YOLO_MODEL_PATH` | `yolo11n.pt` | AI model (auto-downloaded) |
| `DEVICE` | `cuda` / `cpu` | Auto-detected GPU or CPU |
| `PIXELS_PER_METER` | `8.0` | Speed scaling calibration |
| `UI_POLLING_INTERVAL_MS` | `50` | Frontend refresh rate (20 FPS) |
| `LANE_TOP_Y` / `LANE_BOTTOM_Y` | `350` / `720` | Trapezoid road region (720p) |
| `LANE_TOP_X` / `LANE_BOTTOM_X` | `[580..700]` / `[100..1180]` | Perspective lane boundaries |
| `CONGESTION_THRESHOLDS` | `LOW:8, MEDIUM:15` | Vehicle count thresholds |

### Custom Video Source via `.env`
Create a `.env` file (see `.env.example`) to override defaults:
```env
YOLO_MODEL_PATH=yolo11m.pt
```

---

## 🧠 AI & Analytics Pipeline

### Perspective-Aware Lane Detection
Unlike naive vertical splits, the system uses a **trapezoidal road model** that mirrors real camera perspective:
- 5 boundary lines defined at horizon (`LANE_TOP_Y`) and ground (`LANE_BOTTOM_Y`)
- At any vehicle Y-position, boundary X is computed via linear interpolation:
  ```
  x(y) = x_top + (y - y_top) × (x_bottom - x_top) / (y_bottom - y_top)
  ```
- Vehicles are assigned to Lane 1–4 based on centroid position relative to these slanted boundaries

### Speed Estimation
```
speed_km/h = (pixel_displacement / PIXELS_PER_METER / Δt) × 3.6
```
- Smoothed over a 5-frame rolling window to filter tracking jitter
- Clamped to `0–120 km/h`; typical readings: **40–75 km/h** for moving traffic

### Prediction Engine (`ml/prediction.py`)
- Moving average over the last 20 frames to predict next vehicle count
- Trend direction (`↑ ↓ →`) computed from linear regression on count history

---

## 📡 API Reference

Backend runs on `http://localhost:8001`. Swagger docs: `http://localhost:8001/docs`

| Endpoint | Method | Description |
|---|---|---|
| `/results/latest` | GET | Current frame metrics (JSON) |
| `/results/history` | GET | Historical traffic records |
| `/frame/latest` | GET | Base64-encoded annotated frame |
| `/health` | GET | System health check |

---

## 📊 Dashboard Features

- **Live Video Feed** — YOLO11-annotated highway stream with:
  - Glowing neon bounding boxes per vehicle
  - Vehicle ID + real-time speed HUD labels
  - Slanted perspective lane separator overlays (L1–L4)
  - Neon motion trails (last 15 positions)
- **Real-Time Metrics** — Vehicle count, congestion level, avg speed, predicted count
- **Zone Health** — Per-sector (Sector Alpha / Beta) vehicle density bars
- **AI Insights** — Situational awareness messages (e.g., "Traffic volume increasing ↑")
- **Intelligence Log** — Scrollable history of traffic snapshots
- **Traffic Flow Chart** — Live vehicle count time-series

---

## 🔧 Manual Inference (CLI)

Run inference on a specific file without the full stack:
```bash
# Process a single image
python scripts/run_inference.py --type image --source data/sample.jpg --name test_run

# Process a video file
python scripts/run_inference.py --type video --source data/highway.mp4 --name highway_cam
```

---

## 🛠️ Performance & Tuning

| Setting | Target | Achieved |
|---|---|---|
| Inference FPS | 30+ | **38 FPS** (NVIDIA GPU) |
| Dashboard FPS | 20+ | **14–20 FPS** |
| End-to-End Latency | <150ms | **70–115ms** |
| Speed Accuracy | 40–80 km/h | **40–75 km/h** |

**Tips to improve performance:**
- Use a larger YOLO model (`yolo11s.pt`, `yolo11m.pt`) for better accuracy
- Use a smaller model (`yolo11n.pt`) for maximum speed on low-end GPUs
- Reduce `imgsz` in `config.py` for faster inference at lower resolution
- Enable `half=True` in `ml/inference.py` for FP16 on NVIDIA Tensor Cores

---

## 📋 Requirements

```
fastapi
uvicorn
sqlalchemy
pydantic
ultralytics          # YOLO11 (latest)
opencv-python-headless
python-multipart
python-dotenv
```

> **PyTorch** must be installed separately with CUDA support for GPU acceleration.

---

## 📝 License

This project was developed as part of the **ET 201 — IoT Systems** course at NIIT University.

---

*Built with ❤️ using YOLO11, FastAPI, and OpenCV*
