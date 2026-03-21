# Cloud-Oriented IoT Traffic Surveillance System (MVP)

A working prototype for processing traffic camera feeds, counting vehicles using YOLO, estimating congestion, and visualizing data on a dashboard.

## Architectural Overview

This system is built with a **Cloud-Oriented Architecture** aligning with modern decoupling practices:
- **Backend (Cloud/Edge Node)**: A FastAPI server that handles all Machine Learning inference (YOLO). **The ML model runs exclusively here.**
- **Frontend (Dashboard)**: A pure HTML/JS dashboard strictly for monitoring metrics and viewing history. It contains no ML logic.

### Supported Modes:
1. **Demo / Prototype Mode**: Simulate sensor input by uploading images or videos via the dashboard UI or directly to the `/analyze/upload` API endpoint.
2. **Real Deployment (Sensor/Camera) Mode**: Edge devices (e.g., Raspberry Pi, IP Cameras) can push base64-encoded frames directly to the `/analyze/frame` API endpoint for real-time processing. 

## Setup & Running Locally

1. Ensure you have Python 3.9+ installed.
2. Create and activate a Virtual Environment inside `traffic-surveillance-mvp`:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   # source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Backend API Server:
   ```bash
   python scripts/run_server.py
   ```
   *The server runs on `http://localhost:8000`. You can visit `http://localhost:8000/docs` to see the generated Swagger UI for endpoints.*

5. Open the Frontend Dashboard:
   Open `frontend/index.html` in your web browser. 

## Usage & Testing

### Demo Upload Validation
1. Use the "Demo / Prototype Upload" section on the dashboard.
2. Select an image or video from the `data/` or `dataset/` folder.
3. Click "Analyze File". The image/video will be sent to the backend, processed by YOLO, and the dashboard will automatically update with the results (Vehicle Count and Congestion Level).

### Edge Ingestion Structure (Real Deployment)
You can simulate a real edge device pushing frames by sending a JSON payload to `POST /analyze/frame`:
```json
{
  "source_id": "Main_Street_Cam",
  "frame_id": 1234,
  "image_base64": "<base64_encoded_image_string>"
}
```

## Cloud Deployment Readiness
The separation of the backend from the frontend makes this system easily deployable on cloud platforms like Render, AWS EC2, or Railway.
- The `requirements.txt` contains all necessary python dependencies.
- FastAPI automatically manages the API routing and CORS policies.
- Simply host the backend and update `API_BASE_URL` in `frontend/app.js` to point to the remote cloud server.

## Future Scope
- E-challan generation and Automated Number Plate Recognition (ANPR).
- Advanced traffic rule violation detection.
- Prediction of future congestion using historical data logs.
- Dynamic adaptive signal control based on live metrics.
- Support for PostgreSQL database swapping for long-term production storage.
