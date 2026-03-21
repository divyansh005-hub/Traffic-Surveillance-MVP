import cv2
from ultralytics import YOLO
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

try:
    model = YOLO(config.YOLO_MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load YOLO model: {e}")
    model = None

# Vehicle classes in COCO dataset: 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = [2, 3, 5, 7]

def estimate_congestion(count: int) -> str:
    if count < config.CONGESTION_THRESHOLDS["LOW"]:
        return "LOW"
    elif count <= config.CONGESTION_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    else:
        return "HIGH"

def process_frame(frame) -> tuple[int, str]:
    if model is None:
        raise RuntimeError("YOLO model not loaded")
    
    results = model(frame, classes=VEHICLE_CLASSES, verbose=False)
    
    vehicle_count = 0
    if len(results) > 0:
        boxes = results[0].boxes
        vehicle_count = len(boxes)
        
    congestion = estimate_congestion(vehicle_count)
    return vehicle_count, congestion

def process_image(image_path: str) -> tuple[int, str]:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    return process_frame(img)

def process_video_sample(video_path: str) -> tuple[int, str]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video {video_path}")
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError("Could not read frame from video")
        
    return process_frame(frame)

def analyze_full_video(video_path: str, source_id: str, db_session):
    from backend.database import TrafficResult
    from datetime import datetime
    
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    
    import time
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_id % 30 == 0:
            count, congestion = process_frame(frame)
            
            res = TrafficResult(
                timestamp=datetime.utcnow(),
                source_id=source_id,
                frame_id=frame_id,
                vehicle_count=count,
                congestion_level=congestion
            )
            db_session.add(res)
            db_session.commit()
            print(f"Frame {frame_id}: {count} vehicles -> {congestion}")
            time.sleep(1) # Simulate real-time stream
            
        frame_id += 1
        
    cap.release()
