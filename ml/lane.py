import sys
import os
import cv2
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Global cache for dynamic boundaries
cached_boundaries = None

def detect_lanes(frame):
    """
    Detect lane boundaries using Canny and Hough Transform.
    Returns 3 x-coordinates representing the boundaries at the top and bottom Y.
    Format: [(top_x1, bottom_x1), (top_x2, bottom_x2), (top_x3, bottom_x3)]
    """
    global cached_boundaries
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    height, width = frame.shape[:2]
    
    # Optional: Mask to focus on the road region (bottom 2/3)
    mask = np.zeros_like(edges)
    polygon = np.array([[
        (0, height),
        (width, height),
        (width, int(height * 0.3)),
        (0, int(height * 0.3))
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    masked_edges = cv2.bitwise_and(edges, mask)
    
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=150)
    
    top_y = config.LANE_TOP_Y
    bottom_y = config.LANE_BOTTOM_Y
    
    if lines is not None:
        x_intercepts = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if y2 == y1:
                continue # Ignore horizontal lines
                
            slope = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')
            
            # Filter lines that are roughly vertical/diagonal
            if abs(slope) > 0.5:
                # Calculate x intercept at the middle of the evaluation area
                mid_y = (top_y + bottom_y) / 2
                x_mid = x1 + (mid_y - y1) / slope if slope != float('inf') else x1
                
                # Calculate x intercept at top and bottom
                x_top = x1 + (top_y - y1) / slope if slope != float('inf') else x1
                x_bot = x1 + (bottom_y - y1) / slope if slope != float('inf') else x1
                
                x_intercepts.append((x_mid, x_top, x_bot))
                
        if len(x_intercepts) >= 3:
            # Sort by mid_y x-intercept to find the left-to-right order
            x_intercepts.sort(key=lambda x: x[0])
            
            # Simple clustering to find the 3 main separators
            # We assume the user wants 4 lanes (3 separators)
            # Just take 3 roughly evenly spaced lines or use KMeans.
            # For simplicity, we'll group them into 3 bins if possible
            clusters = []
            for item in x_intercepts:
                found = False
                for c in clusters:
                    if abs(c[0][0] - item[0]) < 50: # 50px threshold
                        c.append(item)
                        found = True
                        break
                if not found:
                    clusters.append([item])
            
            if len(clusters) >= 3:
                # Take the top 3 clusters by size or just the first 3 sorted by X
                clusters.sort(key=lambda x: x[0][0])
                boundaries = []
                # Pick the average of the 3 most prominent clusters (or just first 3)
                for i in range(min(3, len(clusters))):
                    avg_top = np.mean([item[1] for item in clusters[i]])
                    avg_bot = np.mean([item[2] for item in clusters[i]])
                    boundaries.append((avg_top, avg_bot))
                
                if len(boundaries) == 3:
                    cached_boundaries = boundaries
                    return boundaries

    # Fallback to config perspective if no previous cache
    if cached_boundaries is not None:
        return cached_boundaries
        
    return [(config.LANE_TOP_X[i], config.LANE_BOTTOM_X[i]) for i in [1, 2, 3]]

def get_lane_boundary_x(y, idx, dynamic_boundaries=None):
    """Calculates the X-coordinate of a lane boundary at a given Y using linear interpolation."""
    top_y = config.LANE_TOP_Y
    bottom_y = config.LANE_BOTTOM_Y
    
    if dynamic_boundaries and len(dynamic_boundaries) >= 3 and 1 <= idx <= 3:
        top_x, bottom_x = dynamic_boundaries[idx - 1]
    else:
        top_x = config.LANE_TOP_X[idx]
        bottom_x = config.LANE_BOTTOM_X[idx]
    
    if bottom_y == top_y: return top_x
    
    # Simple linear interpolation
    return top_x + (y - top_y) * (bottom_x - top_x) / (bottom_y - top_y)

def assign_lane(centroid, dynamic_boundaries=None):
    """
    Assign vehicle to a lane (1-4) based on perspective-aware boundaries or dynamic ones.
    """
    if not centroid:
        return 0
    
    x, y = centroid
    
    # Check boundaries left-to-right (Indices 1, 2, 3 represent internal separators)
    if x < get_lane_boundary_x(y, 1, dynamic_boundaries):
        return 1
    elif x < get_lane_boundary_x(y, 2, dynamic_boundaries):
        return 2
    elif x < get_lane_boundary_x(y, 3, dynamic_boundaries):
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
