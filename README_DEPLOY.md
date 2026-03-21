# Deployment Guide: Traffic Surveillance MVP 🚀

This project has been fully updated and configured to be a **Production-Ready, Single full-stack Deployment**. 

## What changed?
1. The **FastAPI Backend** now statically serves the Dashboard (`frontend` folder) directly. No more handling two separate servers!
2. The Dashboard's API base URL automatically adapts to the environment it's running in.
3. **Deployment Configurations** (`render.yaml` and `Procfile`) have been added.

## 🚀 One-Click Deployment (Recommended)

Since creating remote platform accounts requires personal credentials, the project is configured for a **zero-configuration deployment on Render**. 

### Deploy to Render
1. Create a free account on [Render.com](https://render.com).
2. Push this repository to GitHub.
3. On Render, click **New +** > **Blueprint**.
4. Connect your GitHub repository.
5. Render will automatically detect the `render.yaml` file and deploy the FastAPI server (which includes the frontend).

*(Alternatively, you can use the **Web Service** option, selecting `Python`, and using `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` as the Start Command).*

### What happens when deployed?
- Your new public URL (e.g., `https://traffic-surveillance-api.onrender.com`) will serve the Dashboard directly.
- The Dashboard will automatically connect to its own backend at that same URL.
- Demo/Upload capabilities will run perfectly using the YOLO model on Render's cloud infrastructure.

## Local Testing
If you want to run the new unified app locally:
```bash
# Run from the project root
.\venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000
```
Then visit `http://localhost:8000` in your browser.
