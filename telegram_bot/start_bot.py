import logging
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(["python", self.script_path])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            logging.info(f"{event.src_path} changed, restarting bot...")
            self.start_bot()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    script_path = "main.py"
    event_handler = ReloadHandler(script_path=script_path)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
