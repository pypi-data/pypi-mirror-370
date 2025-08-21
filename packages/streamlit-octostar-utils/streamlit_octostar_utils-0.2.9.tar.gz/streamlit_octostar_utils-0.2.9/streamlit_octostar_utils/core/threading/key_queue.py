import threading
import time


class KeyQueue:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()
        self._poll_freq = 0.05

    def set(self, key, item):
        with self.lock:
            self.data[key] = item

    def get(self, key, remove=False, timeout=None):
        start_time = time.time()
        with self.lock:
            while key not in self.data:
                if timeout is not None and time.time() - start_time > timeout:
                    raise TimeoutError(f"Timeout while waiting for key '{key}'.")
                self.lock.release()
                time.sleep(self._poll_freq)
                self.lock.acquire()
            value = self.data[key]
            if remove:
                del self.data[key]
            return value

    def get_nowait(self, key, remove=False):
        with self.lock:
            value = self.data[key]
            if remove:
                del self.data[key]
            return value

    def pop(self, timeout=None):
        start_time = time.time()
        with self.lock:
            while not bool(self.data):
                if timeout is not None and time.time() - start_time > timeout:
                    raise TimeoutError(
                        "Timeout while waiting for an item to be available in the queue."
                    )
                self.lock.release()
                time.sleep(self._poll_freq)
                self.lock.acquire()
            key = list(self.data.keys())[0]
            item = self.data.pop(key)
            return key, item

    def is_empty(self):
        with self.lock:
            return not bool(self.data)

    def list_keys(self):
        with self.lock:
            return list(self.data.keys())

    def join(self, timeout=None):
        start_time = time.time()
        while True:
            if self.is_empty():
                break
            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError("Timeout while waiting for the queue to be empty.")
            time.sleep(self._poll_freq)

    def as_dict(self):
        with self.lock:
            return self.data

    def __str__(self):
        with self.lock:
            return str(self.data)
