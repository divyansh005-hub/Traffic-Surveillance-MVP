import argparse
import subprocess
import time
import sys
import os
import signal

def main():
    parser = argparse.ArgumentParser(description="Start all components of the Smart Traffic Intelligence Platform")
    parser.add_argument("--video", type=str, required=True, help="Path to the source video file to process")
    parser.add_argument("--name", type=str, default="live_feed", help="Source Name/ID for the inference")
    parser.add_argument("--port-backend", type=int, default=8001, help="Port for the FastAPI backend")
    parser.add_argument("--port-frontend", type=int, default=8080, help="Port for the frontend server")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video file not found at {args.video}")
        sys.exit(1)

    # Determine paths
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    backend_script = os.path.join(root_dir, "scripts", "run_server.py")
    inference_script = os.path.join(root_dir, "scripts", "run_inference.py")

    processes = []

    try:
        print(">>> Starting FastAPI Backend...")
        backend_proc = subprocess.Popen([sys.executable, backend_script])
        processes.append(("Backend", backend_proc))
        
        print(f">>> Starting Frontend Server on port {args.port_frontend}...")
        frontend_proc = subprocess.Popen([sys.executable, "-m", "http.server", str(args.port_frontend), "--directory", frontend_dir])
        processes.append(("Frontend", frontend_proc))
        
        # Give servers a moment to bind to their ports
        time.sleep(2)
        
        print("\n\n" + "="*50)
        print(f">>> SYSTEM ONLINE.")
        print(f"-> Open your browser to: http://localhost:{args.port_frontend}/")
        print("="*50 + "\n")
        
        print(f">>> Starting YOLO Inference on {args.video}...")
        inference_proc = subprocess.Popen([
            sys.executable, inference_script, 
            "--type", "video", 
            "--source", args.video,
            "--name", args.name
        ])
        processes.append(("Inference", inference_proc))
        
        # Wait for inference to complete
        inference_proc.wait()
        
        print("\n[OK] Inference completed. Shutting down servers...")

    except KeyboardInterrupt:
        print("\n[!] Keyboard interrupt received. Shutting down all components...")
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
