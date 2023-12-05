import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import cv2
import tensorflow as tf
import numpy as np
import os

IMG_SIZE = (300, 150)
CLASSES = ['Bee','Varroa','Wasp'] # the tà đạo way
model = tf.keras.models.load_model('SavedModel')

from pymongo import MongoClient
client = MongoClient("localhost", 27017)
db = client.prediction_database
collection = db.img_classification

class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        print (event)
        time.sleep(0.25)
        img = cv2.imread(event.src_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = tf.image.resize(img, IMG_SIZE)
        #predict image
        yhat = model.predict(np.expand_dims(img, 0))
        prediction = yhat.argmax(axis=-1)[0]
        filename = (event.src_path).split('/')[-1]
        record = {
            "prediction": CLASSES[prediction]
        }
        collection.update_one({'_id':filename},{"$set":record},upsert=True)
        
        print(CLASSES[prediction])
        print(yhat)
        print((event.src_path).split('/'))
        print("==========")
        print(yhat.argmax(axis=-1))

#        yhat = tf.nn.softmax(yhat[0])
#        yhat = np.array(yhat)


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
