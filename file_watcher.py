import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#import cv2
#import tensorflow as tf
#import numpy as np
#import os
#IMG_SIZE = (300, 150)
#CLASSES = ['Bee','Varroa','Wasp'] # the tà đạo way
#model = tf.keras.models.load_model('SavedModel')

#from pymongo import MongoClient
#client = MongoClient("localhost", 27017)
#db = client.prediction_database
#collection = db.img_classification

from driver import run

class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        time.sleep(0.25)
        run(event)
        


if __name__ == "__main__":
    path = "./public/upload"
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
