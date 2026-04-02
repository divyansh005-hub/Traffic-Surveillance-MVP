@echo off
setlocal

:: Ensure system follows UTF-8 for cleaner console output
chcp 65001 >nul

:: Set default video path
set VIDEO="data\BackVehcilesTraffic720p.mp4"
if not "%~1"=="" set VIDEO="%~1"

title Smart Traffic Intelligence Platform - Master Controller

echo ===================================================
echo   Smart Traffic Intelligence Platform - Launching
echo ===================================================
echo.

:: 1. Start Backend in a new window
echo [+] Starting FastAPI Backend (Port 8001)...
start "STCS Backend" cmd /c "echo Starting Backend... && python scripts\run_server.py || pause"

:: 2. Start Frontend in a new window
echo [+] Starting Frontend Dashboard (Port 8080)...
start "STCS Frontend" cmd /c "echo Starting Frontend... && python -m http.server 8080 --directory frontend || pause"

:: 3. Wait for synchronization
echo.
echo [!] Waiting for servers to initialize (5s)...
ping 127.0.0.1 -n 6 >nul

echo.
echo ===================================================
echo  [OK] SYSTEM LIVE
echo  -^> DASHBOARD: http://localhost:8080/
echo  -^> BACKEND:   http://localhost:8001/
echo ===================================================
echo.

:: 4. Start Inference in the current window (to see logs)
echo [+] Starting YOLO Inference Engine on: %VIDEO%
echo [!] Note: Close this window to stop the inference.
echo.
python scripts\run_inference.py --type video --source %VIDEO% --name "live_feed"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] ERROR: Inference Engine exited with code %ERRORLEVEL%.
    pause
)

echo.
echo [OK] Execution finished.
pause
