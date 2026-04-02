import time

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.frame_count = 0
        self.last_frame_time = None
        self.processing_times = []

    def start_frame(self):
        self.start_time = time.perf_counter()

    def end_frame(self):
        duration = time.perf_counter() - self.start_time
        self.processing_times.append(duration)
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)
        self.frame_count += 1
        self.last_frame_time = time.perf_counter()

    def get_fps(self):
        if not self.processing_times:
            return 0.0
        avg_duration = sum(self.processing_times) / len(self.processing_times)
        return round(1.0 / avg_duration if avg_duration > 0 else 0, 2)

    def get_latency(self):
        if not self.processing_times:
            return 0.0
        return round(sum(self.processing_times) / len(self.processing_times) * 1000, 2) # ms
