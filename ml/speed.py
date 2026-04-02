import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def calculate_speed(history, pixels_per_meter=config.PIXELS_PER_METER):
    """
    Calculate speed based on history of positions and timestamps.
    Smoothing displacement over the last few frames to reduce noise.
    history: { 'centroids': [(x,y), ...], 'timestamps': [t, ...] }
    """
    centroids = history.get('centroids', [])
    timestamps = history.get('timestamps', [])
    
    # We need at least 3 points for a stable rolling average
    if len(centroids) < 3:
        return 0.0
    
    # Calculate displacements and time diffs for the last 5 points (or fewer if not available)
    window_size = min(len(centroids), 6)
    recent_centroids = centroids[-window_size:]
    recent_timestamps = timestamps[-window_size:]
    
    speeds_kmh = []
    for i in range(1, len(recent_centroids)):
        p1, t1 = recent_centroids[i-1], recent_timestamps[i-1]
        p2, t2 = recent_centroids[i], recent_timestamps[i]
        
        dt = t2 - t1
        if dt <= 0: continue
        
        # Euclidean distance in pixels
        dist_px = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        # Convert pixels to meters then to km/h (m/s * 3.6 = km/h)
        speed_ms = (dist_px / pixels_per_meter) / dt
        speeds_kmh.append(speed_ms * 3.6)
    
    if not speeds_kmh:
        return 0.0
        
    # Return smoothed average speed in km/h
    avg = float(round(np.mean(speeds_kmh), 2))
    return max(0.0, min(120.0, avg))

def get_average_speed(tracker):
    """Calculates the average speed across all active monitored vehicles."""
    speeds = []
    for vid in tracker.history:
        entry_speeds = tracker.history[vid].get('speeds', [])
        if entry_speeds:
            speeds.append(entry_speeds[-1])
    
    avg = float(round(np.mean(speeds), 2)) if speeds else 0.0
    return max(0.0, min(120.0, avg))
