@echo off
echo =======================================================
echo     IoT Traffic Surveillance System - Live Inference mode
echo =======================================================
echo.
echo Starting the Backend API (Port 8000)...
start "Traffic MVP - Backend API" cmd /k ".\venv\Scripts\activate && python scripts/run_server.py"

echo Starting the Frontend Server (Port 8080)...
start "Traffic MVP - Frontend Dashboard" cmd /k "cd frontend && python -m http.server 8080"

echo.
echo Starting the AI Inference Engine...
echo (Processing video: data\Videos\FrontVehcilesTraffic720p.mp4)
start "Traffic MVP - AI Inference Stream" cmd /k ".\venv\Scripts\activate && python scripts/run_inference.py --source data\Videos\FrontVehcilesTraffic720p.mp4 --type video --name Live_Traffic_Cam_1"

echo.
echo =======================================================
echo All services have been launched!
echo.
echo 1. The Backend API is running on http://localhost:8000
echo 2. The Live Dashboard is hosted at http://localhost:8080
echo 3. The YOLO Live Inference Engine is running in its own window!
echo.
echo Opening the Live Dashboard in your default web browser now...
timeout /t 3 /nobreak >nul
start http://localhost:8080/

echo.
echo The AI Inference script is analyzing the video frame-by-frame and 
echo saving the data. Check the dashboard to watch the "Live Feeds" 
echo table populate in real-time!
echo.
echo To shut everything down later, simply close the 3 command prompt windows that popped up.
echo =======================================================
pause
