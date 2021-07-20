import threading
from threading import Thread
from queue import Queue
from ImgTreatement.TreatImg import process

from Data import DB

class ImgProcessor:
    """
    Class that _process the image in a separate thread
    """
    stopMessage = -1

    def __init__(self, result_callback):
        self._result_callback = result_callback
        self._thread = Thread(target=self.run, args=())
        self._thread.setName("image processing thead")
        self._queue = Queue(maxsize=2)

    def start(self):
        self._thread.start()

    def stop(self):
        self._queue.put(ImgProcessor.stopMessage)

    def run(self):
        while True:
            # get a message for the queue
            msg = self._queue.get(block=True)

            if msg == ImgProcessor.stopMessage:
                break
            elif isinstance(msg, DB.CorrectedImg):
                process(msg)

    def add(self, img: DB.CorrectedImg):
        self._queue.put(img)



