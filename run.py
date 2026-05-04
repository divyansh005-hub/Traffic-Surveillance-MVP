import argparse
import subprocess
import time
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Smart Traffic Intelligence Platform - Master Controller")
    parser.add_argument("--video", type=str, help="Path to the source video file (default: samples/traffic.mp4)")
    parser.add_argument("--name", type=str, default="live_feed", help="Source Name/ID for the inference")
    parser.add_argument("--port-backend", type=int, default=8001, help="Port for the FastAPI backend")
    parser.add_argument("--port-frontend", type=int, default=8080, help="Port for the frontend server")
    
    args = parser.parse_args()
    
    # Default video if not provided
    video_path = args.video
    if not video_path:
        # Check for a sample video
        sample_path = Path("data/samples/traffic.mp4")
        if sample_path.exists():
            video_path = str(sample_path)
        else:
            print("Error: No video source provided. Use --video path/to/video.mp4")
            sys.exit(1)

    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        sys.exit(1)

    # Determine paths
    root_dir = Path(__file__).resolve().parent
    frontend_dir = root_dir / "frontend"
    backend_script = root_dir / "scripts" / "run_server.py"
    inference_script = root_dir / "scripts" / "run_inference.py"

    processes = []

    try:
        print("\n" + "="*50)
        print("  SMART TRAFFIC INTELLIGENCE PLATFORM (STIP)")
        print("="*50 + "\n")

        print(">>> [1/3] Starting FastAPI Backend...")
        backend_proc = subprocess.Popen([sys.executable, str(backend_script)])
        processes.append(("Backend", backend_proc))
        
        print(f">>> [2/3] Starting Frontend Server on port {args.port_frontend}...")
        frontend_proc = subprocess.Popen([sys.executable, "-m", "http.server", str(args.port_frontend), "--directory", str(frontend_dir)])
        processes.append(("Frontend", frontend_proc))
        
        # Give servers a moment to bind
        time.sleep(3)
        
        print("\n" + "*"*50)
        print(f"  SYSTEM ONLINE.")
        print(f"  Dashboard: http://localhost:{args.port_frontend}/")
        print(f"  API Docs:  http://localhost:{args.port_backend}/docs")
        print("*"*50 + "\n")
        
        print(f">>> [3/3] Starting YOLO Inference Engine...")
        print(f"    Source: {video_path}")
        
        inference_proc = subprocess.Popen([
            sys.executable, str(inference_script), 
            "--type", "video", 
            "--source", video_path,
            "--name", args.name
        ])
        processes.append(("Inference", inference_proc))
        
        # Wait for inference to complete
        inference_proc.wait()
        
        print("\n[OK] Inference stream ended. Shutting down system...")

    except KeyboardInterrupt:
        print("\n[!] Emergency shutdown initiated...")
    finally:
        # Cleanup all child processes
        for name, proc in processes:
            if proc.poll() is None:
                print(f"Terminating {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("[OK] All systems offline.")

if __name__ == "__main__":
    main()
