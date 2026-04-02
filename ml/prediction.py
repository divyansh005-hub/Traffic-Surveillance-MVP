import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def predict_next_count(history_counts):
    """
    Predict next vehicle count using simple moving average.
    """
    if not history_counts:
        return 0
    
    window = config.PREDICTION_WINDOW
    recent = history_counts[-window:]
    
    # Simple moving average
    prediction = int(np.mean(recent))
    return prediction

def predict_congestion(predicted_count):
    """
    Predict congestion level based on predicted count.
    """
    if predicted_count < config.CONGESTION_THRESHOLDS["LOW"]:
        return "LOW"
    elif predicted_count <= config.CONGESTION_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    else:
        return "HIGH"

def analyze_trend(history_counts):
    """
    Analyze direction of traffic counts.
    """
    if len(history_counts) < 5:
        return "→"
    
    recent = history_counts[-5:]
    diff = recent[-1] - recent[0]
    
    if diff >= 3:
        return "↑"
    elif diff <= -3:
        return "↓"
    return "→"
