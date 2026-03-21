from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import database
from ml import inference
import config
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Traffic Surveillance MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/results/latest")
def get_latest_result(db: Session = Depends(database.get_db)):
    result = db.query(database.TrafficResult).order_by(desc(database.TrafficResult.timestamp)).first()
    if not result:
        return {"message": "No data available"}
    return {
        "timestamp": result.timestamp.isoformat() + "Z",
        "source_id": result.source_id,
        "frame_id": result.frame_id,
        "vehicle_count": result.vehicle_count,
        "congestion_level": result.congestion_level
    }

@app.get("/results/history")
def get_history(limit: int = 20, db: Session = Depends(database.get_db)):
    results = db.query(database.TrafficResult).order_by(desc(database.TrafficResult.timestamp)).limit(limit).all()
    return [{
        "timestamp": r.timestamp.isoformat() + "Z",
        "source_id": r.source_id,
        "frame_id": r.frame_id,
        "vehicle_count": r.vehicle_count,
        "congestion_level": r.congestion_level
    } for r in results]

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    temp_path = config.DATA_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        count, congestion = inference.process_image(str(temp_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    db_result = database.TrafficResult(
        timestamp=datetime.utcnow(),
        source_id=file.filename,
        frame_id=1,
        vehicle_count=count,
        congestion_level=congestion
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return {
        "timestamp": db_result.timestamp.isoformat() + "Z",
        "source_id": db_result.source_id,
        "frame_id": db_result.frame_id,
        "vehicle_count": db_result.vehicle_count,
        "congestion_level": db_result.congestion_level
    }

@app.post("/analyze/video")
async def analyze_video(source_id: str, video_path: str, db: Session = Depends(database.get_db)):
    try:
        count, congestion = inference.process_video_sample(video_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    db_result = database.TrafficResult(
        timestamp=datetime.utcnow(),
        source_id=source_id,
        frame_id=1,
        vehicle_count=count,
        congestion_level=congestion
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return {
        "message": "Processed video sample",
        "data": {
            "vehicle_count": count,
            "congestion_level": congestion
        }
    }

from pydantic import BaseModel

class FramePayload(BaseModel):
    source_id: str
    frame_id: int
    image_base64: str

@app.post("/analyze/upload")
async def analyze_upload(file: UploadFile = File(...), source_name: str = "demo_upload", db: Session = Depends(database.get_db)):
    """Prototype / Demo mode upload endpoint."""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    temp_path = config.DATA_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        if file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            count, congestion = inference.process_video_sample(str(temp_path))
        else:
            count, congestion = inference.process_image(str(temp_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    db_result = database.TrafficResult(
        timestamp=datetime.utcnow(),
        source_id=source_name,
        frame_id=1, # Demo uploads usually don't have a reliable frame stream ID
        vehicle_count=count,
        congestion_level=congestion
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return {
        "message": "Upload processed successfully",
        "data": {
            "timestamp": db_result.timestamp.isoformat() + "Z",
            "source_id": db_result.source_id,
            "vehicle_count": db_result.vehicle_count,
            "congestion_level": db_result.congestion_level
        }
    }

@app.post("/analyze/frame")
async def analyze_frame(payload: FramePayload, db: Session = Depends(database.get_db)):
    """Real deployment mode: endpoint for edge devices to push frames."""
    try:
        import base64
        import cv2
        import numpy as np
        
        img_data = base64.b64decode(payload.image_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Invalid image data")
            
        count, congestion = inference.process_frame(frame)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Frame processing error: {str(e)}")
        
    db_result = database.TrafficResult(
        timestamp=datetime.utcnow(),
        source_id=payload.source_id,
        frame_id=payload.frame_id,
        vehicle_count=count,
        congestion_level=congestion
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return {
        "status": "success",
        "vehicle_count": count,
        "congestion_level": congestion,
        "timestamp": db_result.timestamp.isoformat() + "Z"
    }
