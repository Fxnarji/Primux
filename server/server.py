import threading
import uvicorn
from fastapi import FastAPI
from core.util import ConfigHelper

class Server:
    def __init__(self):
        self.config = ConfigHelper()
        self.app = FastAPI()
        self.host = self.config.get("host")
        self.port = self.config.get("port")
        print(self.host, self.port)
        self.thread = None
        self._running = False

    def _run_server(self):
        self._running = True
        try:
            uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")
        finally:
            self._running = False

    def start(self):
        if self.thread and self.thread.is_alive():
            print("Server already running")
            return

        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def get_status(self):
        if self.thread and self.thread.is_alive() and self._running:
            return "running"
        else:
            return "stopped"
