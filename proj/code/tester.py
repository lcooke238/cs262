from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import logging

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
path = '.'
event_handler = LoggingEventHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()
print('here')
command = input(f"Gimme something > ")