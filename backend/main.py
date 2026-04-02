from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
import json
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import database
from ml import inference
import config

app = FastAPI(title="Smart Traffic Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_latest_metrics():
    path = config.DATA_DIR / "latest_metrics.json"
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/results/latest")
def get_latest_result(db: Session = Depends(database.get_db)):
    # Try to get real-time metrics first
    metrics = get_latest_metrics()
    
    if not metrics:
        # Fallback to DB
        result = db.query(database.TrafficResult).order_by(desc(database.TrafficResult.timestamp)).first()
        if not result:
            return {"message": "No data available"}
        metrics = {
            "timestamp": result.timestamp.isoformat() + "Z",
            "vehicle_count": result.vehicle_count,
            "congestion_level": result.congestion_level,
            "avg_speed": result.avg_speed,
            "density": result.density,
            "flow_rate": result.flow_rate,
            "fps": result.fps,
            "latency": result.latency,
            "predicted_count": result.predicted_count,
            "predicted_congestion": result.predicted_congestion,
            "trend": "→",
            "avg_confidence": 0.0,
            "detection_count": 0,
            "insights": ["Restored from backup data"]
        }

    # Add frame
    frame_path = config.DATA_DIR / "latest_frame.txt"
    if frame_path.exists():
        try:
            with open(frame_path, "r") as f:
                metrics["frame"] = f.read()
        except:
            metrics["frame"] = ""
            
    return metrics

@app.get("/metrics")
def get_metrics_only():
    return get_latest_metrics()

@app.get("/frame")
def get_frame():
    frame_path = config.DATA_DIR / "latest_frame.txt"
    if frame_path.exists():
        with open(frame_path, "r") as f:
            return {"frame": f.read()}
    return {"frame": ""}

@app.get("/prediction")
def get_prediction():
    m = get_latest_metrics()
    return {
        "predicted_count": m.get("predicted_count", 0),
        "predicted_congestion": m.get("predicted_congestion", "N/A")
    }

@app.get("/performance")
def get_performance():
    m = get_latest_metrics()
    return {
        "fps": m.get("fps", 0),
        "latency": m.get("latency", 0)
    }

@app.get("/tracking")
def get_tracking():
    # Return count and lane information
    m = get_latest_metrics()
    return {
        "vehicle_count": m.get("vehicle_count", 0),
        "lane_changes": m.get("total_lane_changes", 0),
        "lane_stats": m.get("lane_stats", {})
    }

@app.get("/results/history")
def get_history(limit: int = 20, db: Session = Depends(database.get_db)):
    results = db.query(database.TrafficResult).order_by(desc(database.TrafficResult.timestamp)).limit(limit).all()
    return [{
        "timestamp": r.timestamp.isoformat() + "Z",
        "vehicle_count": r.vehicle_count,
        "congestion_level": r.congestion_level,
        "avg_speed": r.avg_speed,
        "flow_rate": r.flow_rate,
        "density": r.density
    } for r in results]

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    temp_path = config.DATA_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        m = inference.process_image(str(temp_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    db_result = database.TrafficResult(
        timestamp=datetime.utcnow(),
        source_id=file.filename,
        frame_id=1,
        vehicle_count=m["vehicle_count"],
        congestion_level=m["congestion_level"],
        avg_speed=str(m["avg_speed"]),
        density=m["density"],
        flow_rate=m["flow_rate"],
        fps=str(m["fps"]),
        latency=str(m["latency"]),
        predicted_count=m["predicted_count"],
        predicted_congestion=m["predicted_congestion"]
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return m

@app.post("/analyze/video")
async def analyze_video(source_id: str, video_path: str, db: Session = Depends(database.get_db)):
    try:
        m = inference.process_video_sample(video_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "message": "Processed video sample",
        "data": m
    }
