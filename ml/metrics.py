import time

class FlowMonitor:
    def __init__(self, window_seconds=60):
        self.seen_ids = set()
        self.entry_times = {} # {id: time}
        self.window = window_seconds
        self.flow_history = [] # [(time, count), ...]

    def update(self, current_ids):
        now = time.time()
        new_ids = [vid for vid in current_ids if vid not in self.seen_ids]
        
        for vid in new_ids:
            self.seen_ids.add(vid)
            self.entry_times[vid] = now
            self.flow_history.append(now)

        # Cleanup history older than window
        self.flow_history = [t for t in self.flow_history if now - t < self.window]

    def get_flow_rate(self):
        """Returns vehicles per minute."""
        return len(self.flow_history)

def calculate_density(vehicle_count, area_pixels=1280*720):
    """
    Very basic density: vehicles per 1000 pixels.
    In real world: vehicles per km.
    """
    if vehicle_count == 0:
        return 0
    return round((vehicle_count / area_pixels) * 100000, 2)
