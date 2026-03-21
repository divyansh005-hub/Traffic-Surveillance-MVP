import sys
import os
import base64
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app
from fastapi.testclient import TestClient
import config

client = TestClient(app)

def run_checks():
    print("1. Testing /health...")
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    print("   -> OK")

    print("\n2. Creating a blank test image...")
    # Create blank image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.imwrite("test_blank.jpg", img)

    print("\n3. Testing /analyze/upload (Image)...")
    with open("test_blank.jpg", "rb") as f:
        resp = client.post("/analyze/upload?source_name=test_image", files={"file": ("test_blank.jpg", f, "image/jpeg")})
    assert resp.status_code == 200, f"Image upload failed: {resp.text}"
    data = resp.json()
    assert "vehicle_count" in data["data"]
    print("   -> OK, count:", data["data"]["vehicle_count"])

    print("\n4. Testing /analyze/upload (Video - simulated by passing image to process_video_sample mock or actual small video)...")
    # create a dummy video frame and save as mp4
    out = cv2.VideoWriter('test_blank.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 1, (640, 480))
    out.write(img)
    out.release()
    
    with open("test_blank.mp4", "rb") as f:
        resp = client.post("/analyze/upload?source_name=test_video", files={"file": ("test_blank.mp4", f, "video/mp4")})
    assert resp.status_code == 200, f"Video upload failed: {resp.text}"
    data = resp.json()
    assert "vehicle_count" in data["data"]
    print("   -> OK, count:", data["data"]["vehicle_count"])

    print("\n5. Testing /analyze/frame (Sensor/Camera Edge simulator)...")
    # Base64 encode the blank image
    _, buffer = cv2.imencode('.jpg', img)
    b64 = base64.b64encode(buffer).decode('utf-8')
    payload = {
        "source_id": "Edge_Node_1",
        "frame_id": 100,
        "image_base64": b64
    }
    resp = client.post("/analyze/frame", json=payload)
    assert resp.status_code == 200, f"Frame ingestion failed: {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    print("   -> OK, count:", data["vehicle_count"])

    print("\n6. Checking /results/history...")
    resp = client.get("/results/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 3, "Should have at least 3 historical results."
    print("   -> OK, history contains items from edges and uploads.")

    print("\nAll Endpoints Validated Successfully!")

if __name__ == "__main__":
    try:
        run_checks()
    finally:
        if os.path.exists("test_blank.jpg"): os.remove("test_blank.jpg")
        if os.path.exists("test_blank.mp4"): os.remove("test_blank.mp4")
