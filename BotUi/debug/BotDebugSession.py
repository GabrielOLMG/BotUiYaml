import threading

class DebugSession:
    def __init__(self):
        self.event = threading.Event()
        self.response = None
        self.session_id = None