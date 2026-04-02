import cv2
from ultralytics import YOLO
import sys
import os
import base64
import json
import time
from datetime import datetime
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from ml import tracking, speed, lane, prediction, performance, metrics

# Initialize models and monitors
try:
    model = YOLO(config.YOLO_MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load YOLO model: {e}")
    model = None

tracker = tracking.Tracker()
perf = performance.PerformanceMonitor()
flow = metrics.FlowMonitor(window_seconds=config.TRAFFIC_FLOW_WINDOW)

# Vehicle classes in COCO dataset: 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = [2, 3, 5, 7]

# For prediction history
count_history = []

def estimate_congestion(count: int) -> str:
    if count < config.CONGESTION_THRESHOLDS["LOW"]:
        return "LOW"
    elif count <= config.CONGESTION_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    else:
        return "HIGH"

def safe_replace(temp_path, final_path, max_retries=3):
    """Safely replace a file with minor retries for Windows locks."""
    for i in range(max_retries):
        try:
            os.replace(temp_path, final_path)
            return True
        except PermissionError:
            time.sleep(0.005)
    return False

def process_frame(frame) -> dict:
    if model is None:
        raise RuntimeError("YOLO model not loaded")
    
    perf.start_frame()
    
    # Run YOLO tracking with hardware acceleration and optimized resolution
    results = model.track(
        frame, 
        classes=VEHICLE_CLASSES, 
        persist=True, 
        verbose=False, 
        device=config.DEVICE, 
        imgsz=320, 
        half=True
    )
    
    current_ids = []
    total_lane_changes = 0
    
    if len(results) > 0 and results[0].boxes.id is not None:
        boxes = results[0].boxes
        ids = boxes.id.cpu().numpy().astype(int)
        coords = boxes.xywh.cpu().numpy() # centroid x, y, w, h
        
        for vid, box in zip(ids, coords):
            current_ids.append(vid)
            centroid = (box[0], box[1])
            
            # 1. Update Lane
            v_lane = lane.assign_lane(centroid)
            
            # 2. Update Tracker
            tracker.update(vid, centroid, v_lane)
            
            # 3. Calculate Speed
            v_speed = speed.calculate_speed(tracker.get_history(vid))
            tracker.add_speed(vid, v_speed)
            
            # 4. Lane Change Detection
            if lane.detect_lane_change(tracker.get_history(vid)):
                total_lane_changes += 1

    # Cleanup old tracks
    tracker.cleanup(current_ids)
    flow.update(current_ids)
    
    # 5. Aggregate Lane Statistics
    lane_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    # Count current vehicles per lane
    for vid in current_ids:
        hist = tracker.get_history(vid)
        if hist and hist.get('lanes'):
            v_lane = hist['lanes'][-1]
            if 1 <= v_lane <= 4:
                lane_counts[v_lane] += 1
    
    lane_stats = {}
    for l_id in range(1, 5):
        l_density = lane.calculate_lane_density(lane_counts, l_id)
        lane_stats[str(l_id)] = {
            "count": lane_counts[l_id],
            "density": l_density
        }

    # 6. Aggregate Global Metrics
    vehicle_count = len(current_ids)
    congestion = estimate_congestion(vehicle_count)
    avg_speed = speed.get_average_speed(tracker)
    density = metrics.calculate_density(vehicle_count)
    flow_rate = flow.get_flow_rate()
    
    # Prediction
    count_history.append(vehicle_count)
    if len(count_history) > config.PREDICTION_WINDOW * 2:
        count_history.pop(0)
    
    pred_count = prediction.predict_next_count(count_history)
    pred_congestion = prediction.predict_congestion(pred_count)
    trend = prediction.analyze_trend(count_history)
    
    perf.end_frame()
    
    avg_conf = 0.0
    det_count = 0
    if len(results) > 0 and results[0].boxes.conf is not None:
        confs = results[0].boxes.conf.cpu().numpy()
        if len(confs) > 0:
            avg_conf = float(round(np.mean(confs) * 100, 2))
            det_count = len(confs)
            
    insights = []
    if trend == "↑": insights.append("Traffic volume increasing ↑")
    elif trend == "↓": insights.append("Traffic volume decreasing ↓")
    
    if avg_speed < 15 and vehicle_count >= config.CONGESTION_THRESHOLDS.get("MEDIUM", 15):
        insights.append("Average speed below normal")
        
    for l_id, stats in lane_stats.items():
        if stats["density"] > 75:
            insights.append(f"Lane {l_id} overloaded")
            
    if not insights:
        insights.append("Traffic flow stable")
    
    metrics_data = {
        "vehicle_count": vehicle_count,
        "congestion_level": congestion,
        "avg_speed": avg_speed,
        "total_lane_changes": total_lane_changes,
        "density": density,
        "flow_rate": flow_rate,
        "fps": perf.get_fps(),
        "latency": perf.get_latency(),
        "predicted_count": pred_count,
        "predicted_congestion": pred_congestion,
        "trend": trend,
        "avg_confidence": avg_conf,
        "detection_count": det_count,
        "insights": insights,
        "lane_stats": lane_stats,
        "timestamp": datetime.now().isoformat()
    }

    # Save metrics to JSON for frontend
    metrics_path = config.DATA_DIR / "latest_metrics.json"
    temp_metrics_path = config.DATA_DIR / "latest_metrics_temp.json"
    with open(temp_metrics_path, "w") as f:
        json.dump(metrics_data, f)
    safe_replace(temp_metrics_path, metrics_path)

    # Encode & Save Frame
    try:
        annotated_frame = frame.copy()
        height, width = annotated_frame.shape[:2]
        lane_w = width // 4
        
        # Draw Perspective Lane boundaries (Internal separators 1, 2, 3)
        for i in range(1, 4):
            x_top = int(lane.get_lane_boundary_x(config.LANE_TOP_Y, i))
            x_bottom = int(lane.get_lane_boundary_x(config.LANE_BOTTOM_Y, i))
            cv2.line(annotated_frame, (x_top, config.LANE_TOP_Y), (x_bottom, config.LANE_BOTTOM_Y), (150, 150, 150), 2)
            cv2.putText(annotated_frame, f"L {i}", (x_bottom - 50, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(annotated_frame, "L 4", (width - 100, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
        # Draw vehicle boxes and trails
        if len(results) > 0 and results[0].boxes.id is not None:
            ids_draw = results[0].boxes.id.cpu().numpy().astype(int)
            xyxy = results[0].boxes.xyxy.cpu().numpy()
            
            # 1. Batch draw semi-transparent glowing boxes (massive speed boost)
            overlay = annotated_frame.copy()
            for d_vid, box_xyxy in zip(ids_draw, xyxy):
                x1, y1, x2, y2 = map(int, box_xyxy)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 229, 255), cv2.FILLED)
            cv2.addWeighted(overlay, 0.2, annotated_frame, 0.8, 0, annotated_frame)

            for d_vid, box_xyxy in zip(ids_draw, xyxy):
                x1, y1, x2, y2 = map(int, box_xyxy)
                hist = tracker.get_history(d_vid)
                
                # Trail physics (Smoothed & Truncated)
                if hist and 'centroids' in hist and len(hist['centroids']) > 1:
                    # Truncate to last 15 points to improve clarity
                    trail_pts = hist['centroids'][-15:]
                    pts = np.array(trail_pts, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [pts], isClosed=False, color=(0, 229, 255), thickness=2)
                
                # Glow & HUD Labels
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 229, 255), 3) # Glow
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 255, 255), 1) # Core
                
                spd = 0.0
                if hist and 'speeds' in hist and len(hist['speeds']) > 0:
                    spd = round(hist['speeds'][-1], 1)
                
                # HUD Label positioning standard
                label = f"ID:{d_vid} | {spd} km/h"
                cv2.putText(annotated_frame, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # 2. Resize final frame to reduce Base64 / Disk IO overhead (640p width)
        streaming_frame = cv2.resize(annotated_frame, (640, int(height * (640 / width))))
        _, buffer = cv2.imencode('.jpg', streaming_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        frame_path = config.DATA_DIR / "latest_frame.txt"
        temp_frame_path = config.DATA_DIR / "latest_frame_temp.txt"
        with open(temp_frame_path, "w") as f:
            f.write(frame_base64)
        safe_replace(temp_frame_path, frame_path)
    except Exception as e:
        print(f"Error saving frame: {e}")
        
    return metrics_data

def process_image(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    return process_frame(img)

def process_video_sample(video_path: str) -> dict:
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
    
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret: break
            
        # Process every frame for maximum smoothness
        m_data = process_frame(frame)
        
        # Save to DB every 30 processed frames
        if frame_id % 30 == 0:
                res = TrafficResult(
                    timestamp=datetime.utcnow(),
                    source_id=source_id,
                    frame_id=frame_id,
                    vehicle_count=m_data["vehicle_count"],
                    congestion_level=m_data["congestion_level"],
                    avg_speed=str(m_data["avg_speed"]),
                    total_lane_changes=m_data["total_lane_changes"],
                    density=m_data["density"],
                    flow_rate=m_data["flow_rate"],
                    fps=str(m_data["fps"]),
                    latency=str(m_data["latency"]),
                    predicted_count=m_data["predicted_count"],
                    predicted_congestion=m_data["predicted_congestion"]
                )
                db_session.add(res)
                db_session.commit()
                print(f"Frame {frame_id}: {m_data['vehicle_count']} vehicles, {m_data['avg_speed']} km/h, {m_data['fps']} FPS")
                
        # Removed artificial delay for high-performance GPU mode
        
    cap.release()
