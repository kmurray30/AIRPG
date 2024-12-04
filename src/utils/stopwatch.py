import time

class Stopwatch:
    start_time: float
    last_time: float

    def __init__(self):
        self.start_time = time.time()
        self.last_time = None
    
    def check_second_tick(self):
        if self.last_time is None:
            self.last_time = time.time()
        if time.time() - self.last_time >= 1:
            self.last_time = time.time()
            return True
        return False