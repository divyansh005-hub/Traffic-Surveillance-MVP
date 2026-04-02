import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class Tracker:
    """
    Stateful storage for tracked vehicles.
    History entry: { 'centroids': [], 'timestamps': [], 'lanes': [], 'speeds': [] }
    """
    def __init__(self):
        self.history = {}
        self.limit = config.HISTORY_LIMIT

    def update(self, vehicle_id, centroid, lane=None):
        if vehicle_id not in self.history:
            self.history[vehicle_id] = {
                'centroids': [],
                'timestamps': [],
                'lanes': [],
                'speeds': []
            }
        
        entry = self.history[vehicle_id]
        entry['centroids'].append(centroid)
        entry['timestamps'].append(time.time())
        if lane:
            entry['lanes'].append(lane)
            
        # Maintain history limit
        if len(entry['centroids']) > self.limit:
            for key in entry:
                if entry[key]:
                    entry[key].pop(0)

    def add_speed(self, vehicle_id, speed):
        if vehicle_id in self.history:
            self.history[vehicle_id]['speeds'].append(speed)
            if len(self.history[vehicle_id]['speeds']) > self.limit:
                self.history[vehicle_id]['speeds'].pop(0)

    def get_history(self, vehicle_id):
        return self.history.get(vehicle_id, {})

    def cleanup(self, active_ids):
        # Remove tracks not present in current frame
        inactive = [vid for vid in self.history if vid not in active_ids]
        for vid in inactive:
            del self.history[vid]
