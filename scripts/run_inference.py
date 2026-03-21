import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from backend.database import SessionLocal, Base, engine
from ml.inference import process_image, analyze_full_video
from datetime import datetime
from backend.database import TrafficResult

def main():
    parser = argparse.ArgumentParser(description="Run YOLO Inference on Traffic Data")
    parser.add_argument("--source", type=str, required=True, help="Path to image or video file")
    parser.add_argument("--type", type=str, choices=["image", "video"], required=True, help="Type of input data")
    parser.add_argument("--name", type=str, default="local_run", help="Source ID/Name")
    
    args = parser.parse_args()
    db = SessionLocal()
    
    if args.type == "image":
        count, congestion = process_image(args.source)
        res = TrafficResult(
            timestamp=datetime.utcnow(),
            source_id=args.name,
            frame_id=1,
            vehicle_count=count,
            congestion_level=congestion
        )
        db.add(res)
        db.commit()
        print(f"Image Processed: {count} vehicles detected. Congestion: {congestion}")
    elif args.type == "video":
        print(f"Starting video processing for {args.source}...")
        analyze_full_video(args.source, args.name, db)
        print("Video processing complete.")

if __name__ == "__main__":
    main()
