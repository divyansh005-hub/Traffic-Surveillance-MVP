import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_lane_boundary_x(y, idx):
    """Calculates the X-coordinate of a lane boundary at a given Y using linear interpolation."""
    top_y = config.LANE_TOP_Y
    bottom_y = config.LANE_BOTTOM_Y
    top_x = config.LANE_TOP_X[idx]
    bottom_x = config.LANE_BOTTOM_X[idx]
    
    if bottom_y == top_y: return top_x
    
    # Simple linear interpolation for perspective slanted lines
    return top_x + (y - top_y) * (bottom_x - top_x) / (bottom_y - top_y)

def assign_lane(centroid):
    """
    Assign vehicle to a lane (1-4) based on perspective-aware boundaries.
    """
    if not centroid:
        return 0
    
    x, y = centroid
    
    # Check boundaries left-to-right (Indices 1, 2, 3 represent internal separators)
    if x < get_lane_boundary_x(y, 1):
        return 1
    elif x < get_lane_boundary_x(y, 2):
        return 2
    elif x < get_lane_boundary_x(y, 3):
        return 3
    else:
        return 4

def calculate_lane_density(lane_counts, lane_id):
    """
    Calculate density percentage for a specific lane.
    Assuming max capacity per lane region is ~8 vehicles for 'Critical' level.
    """
    count = lane_counts.get(lane_id, 0)
    # Calibrated max capacity for a single lane segment in view
    MAX_CAPACITY = 10 
    density = (count / MAX_CAPACITY) * 100
    return min(float(round(density, 1)), 100.0)

def detect_lane_change(history):
    """
    Check if the latest lane is different from the previous one.
    """
    lanes = history.get('lanes', [])
    if len(lanes) < 2:
        return False
    
    return lanes[-1] != lanes[-2]
