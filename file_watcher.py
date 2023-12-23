import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from driver import run

class EventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not(event.is_directory):
            time.sleep(0.1)
            run(event)
        


if __name__ == "__main__":
    path = "./public/upload"
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("** watchdog is running")
    print ('\n\n~*~*~*~* ====ready!!!==== *~*~*~*~')
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
