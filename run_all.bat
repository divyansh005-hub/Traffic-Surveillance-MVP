@echo off
echo =======================================================
echo     IoT Traffic Surveillance System - 1-Click Start
echo =======================================================
echo.
echo Starting the Backend API (Port 8000)...
start "Traffic MVP - Backend API" cmd /k ".\venv\Scripts\activate && python scripts/run_server.py"

echo Starting the Frontend Server (Port 8080)...
start "Traffic MVP - Frontend Dashboard" cmd /k "cd frontend && python -m http.server 8080"

echo.
echo =======================================================
echo All services have been launched!
echo.
echo 1. The Backend API is running on http://localhost:8000
echo 2. The Live Dashboard is hosted at http://localhost:8080
echo.
echo Opening the Live Dashboard in your default web browser now...
timeout /t 3 /nobreak >nul
start http://localhost:8080/

echo.
echo * Note: You can simulate sensor data by uploading videos/images 
echo directly in the Dashboard's 'Demo / Prototype Upload' section.
echo.
echo To shut everything down later, simply close the 2 command prompt windows that popped up.
echo =======================================================
pause
