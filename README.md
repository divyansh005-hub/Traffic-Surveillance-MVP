# Smart Traffic Intelligence Platform (STIP) 🚦

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![YOLOv11](https://img.shields.io/badge/Inference-YOLOv11-green.svg)](https://github.com/ultralytics/ultralytics)

An industrial-grade, adaptive traffic management and surveillance platform powered by real-time computer vision. STIP provides dynamic lane analysis, congestion prediction, and a premium dashboard for smart city deployments.

---

## 🌟 Key Features

- **Dynamic Lane Detection**: Real-time perspective-aware lane boundary detection using Canny edges and Hough Transforms.
- **Adaptive UI**: High-contrast, premium "Bright Theme" dashboard with glassmorphism elements.
- **YOLOv11 Integration**: State-of-the-art object detection for vehicle classification and tracking.
- **Congestion Analytics**: Intelligent signal preemption based on lane-specific vehicle density.
- **Telemetry Sync**: Real-time synchronization between the ML inference engine and the FastAPI backend.
- **Interactive Simulation**: 8-lane bidirectional intersection simulation reflecting live telemetry.

## 🏗️ Project Structure

```text
.
├── backend/            # FastAPI server & Database logic
├── frontend/           # HTML/JS Dashboard (Stitch UI)
├── ml/                 # Computer Vision & Tracking algorithms
│   ├── inference.py    # YOLOv11 processing loop
│   └── lane.py         # Dynamic lane geometry logic
├── models/             # YOLO Weights (yolo11n.pt, etc.)
├── scripts/            # Utility and maintenance scripts
├── data/               # Persistent storage (SQLite)
├── docs/               # Architecture & Documentation
└── run.py              # Main system entry point
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9 or higher
- NVIDIA GPU with CUDA (recommended)

### 2. Installation
```bash
git clone https://github.com/divyansh005-hub/Traffic-Surveillance-MVP.git
cd Traffic-Surveillance-MVP
pip install -r requirements.txt
```

### 3. Running the System
STIP is designed for ease of use. Simply run the master controller from the root:

```bash
python run.py --video samples/highway_traffic.mp4
```

**Options:**
- `--video`: Path to the input video file.
- `--name`: Identifier for the traffic feed.
- `--port-frontend`: Change dashboard port (default: 8080).

## 📊 Dashboard Access
Once running, the system exposes:
- **Dashboard**: `http://localhost:8080`
- **API Documentation**: `http://localhost:8001/docs`

## 🛠️ Technology Stack
- **Inference**: Ultralytics YOLOv11
- **Backend**: FastAPI, SQLAlchemy (SQLite)
- **Frontend**: Vanilla HTML5/CSS3/JavaScript (Stitch-inspired design)
- **Computer Vision**: OpenCV, NumPy

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Developed for the NIIT University Smart City Initiative.*
