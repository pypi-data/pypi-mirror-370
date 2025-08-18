import threading
import time
import traceback
from enum import Enum
import logging
import streamlit as st

from ..core.threading.key_queue import KeyQueue

logging.basicConfig()
logger = logging.getLogger(__name__)


class AsyncTaskManager:
    max_workers = 10

    class TaskData(object):
        def __init__(self, output_fn, task_id, cancel_event):
            def _output(status, data):
                if self.cancel_event.is_set():
                    raise AsyncTaskManager.CancelledError()
                output_fn(task_id, status, data)

            self.task_id = task_id
            self.cancel_event = cancel_event
            self.output = _output

    class TaskStatus(Enum):
        INIT = 0
        IN_PROGRESS = 1
        CANCELLING = 2
        SUCCESS = 10
        ERROR = 11
        CANCELLED = 12

    class CancelledError(Exception):
        pass

    def __init__(self, max_workers):
        self._poll_freq = 0.05
        self.max_workers = max_workers
        self.workers = []
        self.lock = threading.Lock()
        self.tasks_queue = KeyQueue()
        self.cancellation_tokens = KeyQueue()
        self.results_queue = KeyQueue()
        self.kill_event = threading.Event()
        self._create_workers()

    def _create_workers(self):
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker_thread)
            worker.start()
            self.workers.append(worker)

    def _worker_thread(self):
        while not self.kill_event.is_set():
            try:
                task_id, task_data = self.tasks_queue.pop(timeout=1.0)
            except TimeoutError:
                continue
            task, task_kwargs = task_data
            canc_event = self.cancellation_tokens.get_nowait(task_id)
            try:
                self.output(task_id, AsyncTaskManager.TaskStatus.IN_PROGRESS, None)
                result = task(
                    AsyncTaskManager.TaskData(self.output, task_id, canc_event),
                    **task_kwargs
                )
                self.output(task_id, AsyncTaskManager.TaskStatus.SUCCESS, result)
            except AsyncTaskManager.CancelledError:
                self.output(
                    task_id,
                    AsyncTaskManager.TaskStatus.CANCELLED,
                    self.get_result(task_id)["data"],
                )
            except BaseException as e:
                logger.error("Error for task " + str(task_id))
                traceback.print_exc()
                self.output(task_id, AsyncTaskManager.TaskStatus.ERROR, e)
            finally:
                try:
                    self.cancellation_tokens.get_nowait(task_id, remove=True)
                except KeyError:
                    pass

    @st.cache_resource
    def get_handler(task_type):
        return AsyncTaskManager(AsyncTaskManager.max_workers)

    def output(self, task_id, status, data):
        self.results_queue.set(task_id, {"id": task_id, "status": status, "data": data})

    def submit(self, task_id, task, kwargs={}):
        self.cancel(task_id)
        self.join(task_id)
        self.cancellation_tokens.set(task_id, threading.Event())
        self.tasks_queue.set(task_id, (task, kwargs))
        self.output(task_id, AsyncTaskManager.TaskStatus.INIT, None)
        return True

    def cancel(self, task_id):
        cancelled = False
        try:
            self.tasks_queue.get_nowait(task_id, remove=True)
            self.cancellation_tokens.get_nowait(task_id, remove=True)
            cancelled = True
        except KeyError:
            try:
                canc_token = self.cancellation_tokens.get_nowait(task_id, remove=True)
                canc_token.set()
                cancelled = True
            except KeyError:
                pass
        if cancelled:
            self.output(
                task_id,
                AsyncTaskManager.TaskStatus.CANCELLING,
                self.get_result(task_id)["data"],
            )
        return cancelled

    def cancel_all(self):
        all_task_ids = set(
            self.tasks_queue.list_keys() + self.cancellation_tokens.list_keys()
        )
        for task_id in all_task_ids:
            self.cancel(task_id)

    def join_all(self):
        self.tasks_queue.join()
        self.kill_event.set()
        for worker in self.workers:
            worker.join()

    def get_result(self, task_id):
        return self.results_queue.get_nowait(task_id)

    def join(self, task_id):
        try:
            result = self.get_result(task_id)
            while result["status"].value < 10:
                time.sleep(self._poll_freq)
                result = self.get_result(task_id)
        except KeyError:
            pass
