import queue
from threading import Thread


class ImageGetter:
    """
        Base class for the display. runs in a separate thread
        capture the image and store it in the parameter lastFrame

    """

    def __init__(self, capture):

        self._thread = Thread(target=self.get, args=())
        self._thread.setName("Camera capture")
        self._capture = capture
        self.stopped = False
        self._queue = queue.Queue()

    def start(self):
        self.stopped = False
        self._thread.start()
        return self

    def get(self):
        while not self.stopped:
            grabbed, image = self._capture.read()
            if grabbed:

                if not self._queue.empty():
                    try:
                        self._queue.get_nowait()  # discard previous (unprocessed) frame
                    except queue.Empty:
                        pass
                self._queue.put(image)
            else:
                self.stop()

        self._capture.release()

    def read(self):
        return self._queue.get()

    def stop(self):
        self.stopped = True