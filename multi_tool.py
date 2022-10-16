class Sync():
    def __init__(self, ready_count):
        self.count = 0  # 7=vesc 5=transmit, 3=lidar, 1=zed
        self.ready_count = ready_count
        self.ready = False
        self.timeout = 120
        self.finished = False

    def update(self, key):
        if key + self.count == self.ready_count:
            self.ready = True

    def set_timeout(self, new_timeout):
        self.timeout = new_timeout


class Experiment():
    def __init__(self, threading):
        self.lidar_ready_event = threading.Event(),
        self.zed_ready_event = threading.Event()
        self.transmit_start_event = threading.Event()
        self.transmit_end_event = threading.Event()

    def transmit_ready(self):
        return self.lidar_ready_event and self.zed_ready_event and self.transmit_start_event
