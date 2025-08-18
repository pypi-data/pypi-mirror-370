from pathlib import Path
from celery import Celery
from celery.result import AsyncResult
import celery.signals as celery_signals
from kombu import Queue
from abc import ABC, abstractmethod
import asyncio
import subprocess
from fastapi import Query
import time
import os
import pickle
import atexit
import redis
import uuid
import json
import shutil
import threading
from pottery import Redlock
from pytz import timezone
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import logging

logger = logging.getLogger(__name__)
logging.getLogger("pottery").setLevel(logging.WARNING)
from celery.app.defaults import DEFAULTS as CELERY_DEFAULTS
import urllib

from .fastapi import Route, CommonModels, DefaultErrorRoute


class RedisFileLock:
    def __init__(self, redis_client, file_path, auto_release_time=30):
        self.redis_client = redis_client
        self.file_path = os.path.realpath(file_path)
        self.lock_key = f"file:lock:{urllib.parse.quote(self.file_path)}"
        self.auto_release_time = auto_release_time
        self.lock = Redlock(
            key=self.lock_key,
            masters={self.redis_client},
            auto_release_time=self.auto_release_time,
        )

    def __enter__(self):
        return self.lock.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.lock.__exit__(exc_type, exc_val, exc_tb)


class CeleryQueueConfig:
    def __init__(
        self,
        n_workers=os.cpu_count(),
        max_tasks_in_queue=None,
        max_tasks_per_child=None,
        max_memory_per_child=None,
        **options,
    ):
        self.n_workers = n_workers
        self.max_tasks_in_queue = max_tasks_in_queue
        self.max_tasks_per_child = max_tasks_per_child
        self.max_memory_per_child = max_memory_per_child  # KiB
        self.options = options


class CelerySerialized:
    def __init__(self, folder, redis_client, data=None):
        self.folder = folder
        self.data = data
        self.redis_client = redis_client

    def set_task_id(self, task_id):
        self.task_id = task_id

    def dump(self):
        assert self.task_id
        with RedisFileLock(self.redis_client, os.path.join(self.folder, self.task_id)):
            with open(os.path.join(self.folder, self.task_id), "wb") as target_file:
                pickle.dump(self.data, file=target_file, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self):
        assert self.task_id
        with RedisFileLock(self.redis_client, os.path.join(self.folder, self.task_id)):
            with open(os.path.join(self.folder, self.task_id), "rb") as source_file:
                data = pickle.load(source_file)
        return data


class CeleryExecutor(object):
    class QueueFullException(Exception):
        pass

    AWAITING = "AWAITING"
    STARTED = "STARTED"
    MAX_STARTUP_CHECKS = 20
    CELERY_BROKER_PREFIX = "celery-task-meta-"
    BACKEND_COMM_THREADS_RATIOS = {"get": 0.5, "set": 0.2, "io": 0.3}

    def __init__(
        self,
        name,
        module_name,
        base_folder=os.getcwd(),
        expiration_await=300,
        expiration_ready=3600,
        queue_config=None,
        loglevel="info",
        preload_time_limit=CELERY_DEFAULTS.get("worker_proc_alive_timeout"),
    ):
        # Basic info
        self.name = name
        self.loglevel = loglevel
        self.base_folder = base_folder
        self.filename = module_name
        self.queue_config = queue_config or {"default": CeleryQueueConfig()}
        self.n_workers = sum(queue.n_workers for queue in self.queue_config.values())

        # Helper threadpools setup
        self.get_thread_pool = None
        self.set_thread_pool = None
        self.io_thread_pool = None
        self.queue_threadlocks = {k: threading.Lock() for k in self.queue_config.keys()}

        # Folder setup
        self.base_folder = Path(base_folder).resolve()
        self.root_folder = Path(base_folder).resolve().joinpath("data")
        self.out_folder = self.root_folder.joinpath("out")
        self.in_folder = self.root_folder.joinpath("in")

        # Redis config
        self.redis_host = "127.0.0.1"
        self.redis_port = 6379
        self.redis_process = None
        self.redis_client = redis.StrictRedis(host=self.redis_host, port=self.redis_port)

        # Celery basic config
        self.app = Celery(self.filename)
        self.app.conf.broker_url = f"redis://{self.redis_host}:{self.redis_port}/0"
        self.app.conf.result_backend = f"redis://{self.redis_host}:{self.redis_port}/0"
        self.app.conf.track_started = True
        self.app.conf.task_serializer = "json"
        self.app.conf.result_serializer = "json"
        self.app.conf.accept_content = ["application/json"]
        self.app.conf.task_expires = expiration_await
        self.app.conf.result_expires = expiration_ready
        self.app.conf.backend_cleanup_schedule = max(10, round(expiration_ready / 20))
        self.app.conf.beat_max_loop_interval = max(10, round(expiration_ready / 20))
        self.app.conf.worker_proc_alive_timeout = preload_time_limit
        if f"{os.environ.get('OS_DEV_MODE', 'false')}".lower() == "true":
            self.app.conf.celery_always_eager = True
            self.app.conf.task_always_eager = True
            self.app.conf.task_eager_propagates = True

        self.app.timezone = timezone("UTC")
        self.app.enable_utc = True

        # Queues setup
        self.preload_functions = {}
        self.resource_registry = {}
        self.app.conf.task_queues = [Queue(name, routing_key=name) for name in self.queue_config.keys()]
        self.app.conf.task_default_queue = self.app.conf.task_queues[0].name
        self.app.conf.task_default_routing_key = self.app.conf.task_queues[0].name

        # Celery Executor setup
        self.processes = []
        self.beat_process = None
        self.stop_event = threading.Event()
        atexit.register(self.close)
        self.set_cleanup_task()
        self.register_state_signals()

    def finalize(self):
        self.register_worker_initialization()

    def preload_on_worker_init(self, **kwargs):
        queue = os.environ.get("CELERY_WORKER_QUEUES", "")
        if queue in self.preload_functions:
            logger.info(f"Preloading resources for queue {queue}")
            for preload_func in self.preload_functions[queue]:
                if queue not in self.resource_registry:
                    self.resource_registry[queue] = {}
                self.resource_registry[queue] = {
                    **self.resource_registry[queue],
                    **(preload_func(self.resource_registry[queue]) or {}),
                }
            logger.info(f"All resources preloaded for queue {queue}")

    def set_awaiting_state(self, sender=None, headers=None, **kwargs):
        task_id = headers.get("id") if headers else None
        if not task_id:
            return
        result = AsyncResult(task_id, app=self.app)
        result.backend.store_result(task_id, result=None, state=CeleryExecutor.AWAITING)

    def set_started_state(self, task_id, task, *args, **kwargs):
        result = AsyncResult(task_id, app=self.app)
        result.backend.store_result(task_id, result=None, state=CeleryExecutor.STARTED)

    def register_worker_initialization(self):
        if self.preload_functions:
            celery_signals.worker_process_init.connect(self.preload_on_worker_init)

    def register_state_signals(self):
        celery_signals.before_task_publish.connect(self.set_awaiting_state)
        celery_signals.task_prerun.connect(self.set_started_state)

    def cleanup_task_results(in_dir, out_dir, redis_host, redis_port, task_expires, result_expires):
        logger.info("Starting cleanup of expired task results...")
        redis_client = redis.StrictRedis(host=redis_host, port=redis_port)
        for file_name in os.listdir(in_dir):
            file_path = os.path.join(in_dir, file_name)
            redis_key = f"{CeleryExecutor.CELERY_BROKER_PREFIX}{file_name}"
            if not redis_client.exists(redis_key):
                stale = False
                if os.path.exists(os.path.join(out_dir, file_name)):
                    stale = (time.time() - os.path.getctime(file_path)) > result_expires
                else:
                    stale = (time.time() - os.path.getctime(file_path)) > task_expires
                if stale:
                    try:
                        with RedisFileLock(redis_client, file_path):
                            os.remove(file_path)
                            logger.debug(f"Deleted stale file: {file_path}")
                        with RedisFileLock(redis_client, os.path.join(out_dir, file_name)):
                            if os.path.exists(os.path.join(out_dir, file_name)):
                                os.remove(os.path.join(out_dir, file_name))
                                logger.debug(f"Deleted stale file: {os.path.join(out_dir, file_name)}")
                    except OSError:
                        pass
        for file_name in os.listdir(out_dir):
            file_path = os.path.join(out_dir, file_name)
            redis_key = f"{CeleryExecutor.CELERY_BROKER_PREFIX}{file_name}"
            if not redis_client.exists(redis_key):
                stale = (time.time() - os.path.getctime(file_path)) > task_expires
                if stale:
                    try:
                        with RedisFileLock(redis_client, file_path):
                            os.remove(file_path)
                        with RedisFileLock(redis_client, os.path.join(in_dir, file_name)):
                            if os.path.exists(os.path.join(in_dir, file_name)):
                                os.remove(os.path.join(in_dir, file_name))
                        logger.debug(f"Deleted stale file: {file_path}")
                    except OSError:
                        pass
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=f"{CeleryExecutor.CELERY_BROKER_PREFIX}*")
            if not keys:
                break
            for key in keys:
                if redis_client.ttl(key) == -2:
                    redis_client.delete(key)
                    logger.debug(f"Deleted expired Redis key: {key.decode()}")
            if cursor == 0:
                break
        logger.info("Completed cleanup of expired task results.")

    def set_cleanup_task(self):
        if "celery.backend_cleanup" in self.app.tasks:
            self.app.tasks.pop("celery.backend_cleanup")
        self.app.task(CeleryExecutor.cleanup_task_results, name="celery.backend_cleanup")
        self.app.conf.beat_schedule = {
            "celery.backend_cleanup": {
                "task": "celery.backend_cleanup",
                "schedule": self.app.conf.backend_cleanup_schedule,
                "args": (
                    str(self.in_folder),
                    str(self.out_folder),
                    self.redis_host,
                    self.redis_port,
                    self.app.conf.task_expires,
                    self.app.conf.result_expires,
                ),
            },
        }

    def start(self):
        logger.info("Initializing data folders...")
        shutil.rmtree(self.root_folder, ignore_errors=True)
        for folder in [self.in_folder, self.out_folder]:
            os.makedirs(folder, exist_ok=True)
        logger.info("Starting Redis server...")
        self.redis_process = subprocess.Popen(
            [
                "redis-server",
                "--bind",
                str(self.redis_host),
                "--port",
                str(self.redis_port),
            ]
        )
        attempts_done = 0
        while attempts_done < CeleryExecutor.MAX_STARTUP_CHECKS:
            try:
                self.redis_client.ping()
                break
            except:
                pass
                attempts_done += 1
                time.sleep(1.0)
            if attempts_done == CeleryExecutor.MAX_STARTUP_CHECKS:
                raise TimeoutError("Redis not ready after a long wait!")
        self.redis_client.flushall()
        for queue, queue_config in self.queue_config.items():
            for slot in range(queue_config.n_workers):
                worker_name = f"celery@{self.name}:{queue}:{slot}"
                command = [
                    "env",
                    f"PYTHONPATH={os.getcwd()}",
                    f"CELERY_WORKER_QUEUES={queue}",
                    f"CELERY_WORKER_NAME={worker_name}",
                    "celery",
                    "--app",
                    f"{self.filename}.{self.name}",
                    "worker",
                    "--pool=prefork",
                    "--concurrency=1",
                    f"--loglevel={self.loglevel}",
                    f"-n {worker_name}",
                ]
                if queue_config.max_tasks_per_child is not None:
                    command.append(f"--max-tasks-per-child={queue_config.max_tasks_per_child}")
                if queue_config.max_memory_per_child is not None:
                    command.append(f"--max-memory-per-child={queue_config.max_memory_per_child}")
                process = subprocess.Popen(command)
                self.processes.append(process)
        self.beat_process = subprocess.Popen(
            [
                "celery",
                "--app",
                f"{self.filename}.{self.name}",
                "beat",
                f"--loglevel={self.loglevel}",
            ]
        )
        attempts_done = 0
        while attempts_done < CeleryExecutor.MAX_STARTUP_CHECKS:
            print("Waiting for Celery workers to become ready...")
            try:
                inspector = self.app.control.inspect()
                active_workers = inspector.active()
                if active_workers and len(active_workers) == len(self.processes):
                    print("Celery is ready!")
                    break
            except:
                pass
            attempts_done += 1
            time.sleep(1.0)
            if attempts_done == CeleryExecutor.MAX_STARTUP_CHECKS:
                raise TimeoutError("Celery not ready after a long wait!")
        total_ratio = sum(CeleryExecutor.BACKEND_COMM_THREADS_RATIOS.values())
        normalized_ratios = {
            key: value / total_ratio for key, value in CeleryExecutor.BACKEND_COMM_THREADS_RATIOS.items()
        }
        allocated_workers = {key: round(self.n_workers * ratio) for key, ratio in normalized_ratios.items()}
        while sum(allocated_workers.values()) != self.n_workers:
            diff = self.n_workers - sum(allocated_workers.values())
            key = max(
                allocated_workers,
                key=lambda k: normalized_ratios[k] - (allocated_workers[k] / self.n_workers),
            )
            allocated_workers[key] += diff
        allocated_workers = {k: max(v, 1) for k, v in allocated_workers.items()}
        self.get_thread_pool = ThreadPoolExecutor(max_workers=allocated_workers["get"])
        self.set_thread_pool = ThreadPoolExecutor(max_workers=allocated_workers["set"])
        self.io_thread_pool = ThreadPoolExecutor(max_workers=allocated_workers["io"])

    def close(self):
        if self.processes:
            logger.info("Terminating Celery...")
            for process in self.processes:
                process.terminate()
                process.wait()
                self.processes = []
        if self.beat_process:
            self.beat_process.terminate()
            self.beat_process.wait()
        if self.redis_process:
            logger.info("Stopping Redis server...")
            self.redis_process.terminate()
            self.redis_process.wait()
            self.redis_process = None
        if self.io_thread_pool:
            self.io_thread_pool.shutdown(wait=True)
        if self.get_thread_pool:
            self.get_thread_pool.shutdown(wait=True)
        if self.set_thread_pool:
            self.set_thread_pool.shutdown(wait=True)
        shutil.rmtree(self.root_folder, ignore_errors=True)
        celery_files = [f for f in os.listdir(self.base_folder) if f.startswith("celerybeat-schedule")]
        for file in celery_files:
            with RedisFileLock(self.redis_client, os.path.join(self.base_folder, file)):
                os.remove(os.path.join(self.base_folder, file))

    def serialized_io(self, task_fn):
        @wraps(task_fn)
        def wrapper(task):
            task_id = task.request.id
            serialized_data = CelerySerialized(folder=self.in_folder, redis_client=self.redis_client)
            serialized_data.set_task_id(task_id)
            data = serialized_data.load()
            del serialized_data
            args, kwargs = data.get("args", []), data.get("kwargs", {})

            if self.app.conf.task_always_eager:
                queue = task.request.delivery_info.get("routing_key", self.app.conf.task_default_routing_key)
                if not queue:
                    queue = os.environ.get("CELERY_WORKER_QUEUES", "")
                task.request.resources = (self.resource_registry or {}).get(queue, {})

            queue = task.request.delivery_info.get("routing_key", self.app.conf.task_default_routing_key)
            task.request.resources = (self.resource_registry or {}).get(queue, {})
            out_data = task_fn(task, *args, **kwargs)
            serialized_data = CelerySerialized(folder=self.out_folder, data=out_data, redis_client=self.redis_client)
            serialized_data.set_task_id(task_id)
            serialized_data.dump()
            del serialized_data
            if os.path.isfile(os.path.join(self.in_folder, task_id)):
                with RedisFileLock(self.redis_client, os.path.join(self.in_folder, task_id)):
                    os.remove(os.path.join(self.in_folder, task_id))
            return task_id

        return wrapper

    @staticmethod
    def base_task(celery_executor, *args, **opts):
        def decorator(func):
            if celery_executor:

                @wraps(func)
                def wrapper(task, *task_args, **task_kwargs):
                    return func(task, *task_args, **task_kwargs)

                serialized_func = celery_executor.serialized_io(wrapper)
                task_func = celery_executor.app.task(*args, **opts)(serialized_func)
            else:

                @wraps(func)
                def base_func(*args, **kwargs):
                    return func(None, *args, **kwargs)

                task_func = base_func
            return task_func

        return decorator

    @staticmethod
    def preload(celery_executor, queue, *args, **opts):
        def decorator(func):
            if queue not in celery_executor.preload_functions:
                celery_executor.preload_functions[queue] = []
            celery_executor.preload_functions[queue].append(func)
            return func

        return decorator

    async def send_task(self, task_fn, args=[], kwargs={}, **options) -> str:
        if self.app.conf.task_always_eager and "dev_preload" not in self.app.conf:
            self.preload_on_worker_init()
            self.app.conf.dev_preload = True

        def _write_task_data(in_folder, task_args, task_kwargs, task_id):
            serialized_data = CelerySerialized(
                folder=in_folder,
                data={"args": task_args, "kwargs": task_kwargs},
                redis_client=self.redis_client,
            )
            serialized_data.set_task_id(task_id)
            serialized_data.dump()

        def _send_task(task_fn, task_id, options):
            queue_name = self.app.conf.task_default_routing_key
            queue_name = getattr(task_fn, "queue", queue_name)
            queue_name = options.get("queue", queue_name)
            limit = self.queue_config[queue_name].max_tasks_in_queue
            if limit:
                with self.queue_threadlocks[queue_name]:
                    queue_count = self.redis_client.llen(queue_name)
                if queue_count > limit:
                    raise CeleryExecutor.QueueFullException(
                        f"Queue '{queue_name}' has reached its limit of {limit} tasks!"
                    )
            task_fn.apply_async(task_id=task_id, **options)

        task_id = str(uuid.uuid4())
        try:
            await asyncio.get_running_loop().run_in_executor(
                self.io_thread_pool,
                _write_task_data,
                self.in_folder,
                args,
                kwargs,
                task_id,
            )

            await asyncio.get_running_loop().run_in_executor(
                self.set_thread_pool, _send_task, task_fn, task_id, options
            )

        except asyncio.CancelledError:
            logger.info(f"Cancelling task {task_id} due to disconnect!")
            await self.terminate_task(task_id)
            raise
        return task_id

    async def terminate_task(self, task_id):
        def _terminate_task(celery_app, task_id):
            celery_app.control.revoke(task_id, terminate=True)

        def _remove_task_data(celery_app, in_folder, out_folder, task_id):
            celery_app.AsyncResult(task_id).forget()
            if os.path.isfile(os.path.join(in_folder, task_id)):
                with RedisFileLock(self.redis_client, os.path.join(self.in_folder, task_id)):
                    os.remove(os.path.join(in_folder, task_id))
            if os.path.isfile(os.path.join(out_folder, task_id)):
                with RedisFileLock(self.redis_client, os.path.join(self.out_folder, task_id)):
                    os.remove(os.path.join(out_folder, task_id))

        await asyncio.get_running_loop().run_in_executor(self.set_thread_pool, _terminate_task, self.app, task_id)
        await asyncio.get_running_loop().run_in_executor(
            self.io_thread_pool,
            _remove_task_data,
            self.app,
            self.in_folder,
            self.out_folder,
            task_id,
        )

    async def poll_task_state(self, task_id):
        def _poll_task_state(celery_app, task_id):
            task = celery_app.AsyncResult(task_id)
            ready, state = task.ready(), task.state
            return ready, state

        return await asyncio.get_running_loop().run_in_executor(
            self.get_thread_pool, _poll_task_state, self.app, task_id
        )

    async def get_task_result(self, task_id, remove=False):
        def _try_get_task_data(celery_app, task_id):
            celery_app.AsyncResult(task_id).get()  # will raise if the task raised an exception

        def _read_task_data(out_folder, task_id):
            serialized_data = CelerySerialized(folder=out_folder, redis_client=self.redis_client)
            serialized_data.set_task_id(task_id)
            result = serialized_data.load()
            return result

        def _remove_task_data(celery_app, in_folder, out_folder, task_id):
            celery_app.AsyncResult(task_id).forget()
            if os.path.isfile(os.path.join(in_folder, task_id)):
                with RedisFileLock(self.redis_client, os.path.join(self.in_folder, task_id)):
                    os.remove(os.path.join(in_folder, task_id))
            if os.path.isfile(os.path.join(out_folder, task_id)):
                with RedisFileLock(self.redis_client, os.path.join(self.out_folder, task_id)):
                    os.remove(os.path.join(out_folder, task_id))

        await asyncio.get_running_loop().run_in_executor(self.get_thread_pool, _try_get_task_data, self.app, task_id)
        result = await asyncio.get_running_loop().run_in_executor(
            self.get_thread_pool, _read_task_data, self.out_folder, task_id
        )
        if remove:
            await asyncio.get_running_loop().run_in_executor(
                self.get_thread_pool,
                _remove_task_data,
                self.app,
                self.in_folder,
                self.out_folder,
                task_id,
            )
        return result

    async def send_and_wait_task(self, task_fn, args=[], kwargs={}, timeout=60, **options):
        task_id = await self.send_task(task_fn, args, kwargs, **options)
        ready = False
        state = None
        start_time = time.time()
        try:
            while not ready:
                ready, state = await self.poll_task_state(task_id)
                if state == "PENDING":
                    raise ValueError("Task with given ID does not exist!")
                if time.time() - start_time > timeout:
                    await self.terminate_task(task_id)
                    raise TimeoutError("Task has not completed within the alloted time amount!")
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            logger.info(f"Cancelling task {task_id} due to disconnect!")
            await self.terminate_task(task_id)
            raise
        return await self.get_task_result(task_id, remove=True)


class FastAPICeleryTaskRoute(Route):
    def __init__(self, app, celery_executor, router=None):
        self.app = app
        self._router = router
        self.routed_funcs = []
        self.celery_executor = celery_executor
        self.define_routes()

    def define_routes(self):
        @Route.include(self)
        @Route.route(
            self,
            path="/task/{task_id}",
            methods=["DELETE"],
            summary="Cancel a queued or running task.",
            status_code=200,
            responses=DefaultErrorRoute.error_responses,
        )
        async def delete_task(task_id: str) -> CommonModels.OKResponseModel:
            await self.celery_executor.terminate_task(task_id)
            return CommonModels.OKResponseModel()

        @Route.include(self)
        @Route.route(
            self,
            path="/task/{task_id}",
            methods=["GET"],
            summary="Get task status (and result if available).",
            status_code=200,
            responses=DefaultErrorRoute.error_responses,
        )
        async def get_task(task_id: str, pop: bool = Query(False)) -> CommonModels.DataResponseModel:
            ready, state = await self.celery_executor.poll_task_state(task_id)
            result = None
            exc = None
            if ready:
                try:
                    result = await self.celery_executor.get_task_result(task_id, remove=pop)
                except BaseException as e:
                    exc = e
            data = {}
            assert (
                (state in ["FAILURE", "RETRY", "REVOKED"] and exc is not None)
                or (state in ["SUCCESS"] and exc is None)
                or (state not in ["SUCCESS", "FAILURE", "RETRY", "REVOKED"])
            )
            if state in ["FAILURE", "RETRY", "REVOKED"]:
                error_response = DefaultErrorRoute.format_error(exc, debug=True).body.decode("utf-8")
                data = {
                    "task_state": state,
                    "task_id": task_id,
                    "data": json.loads(error_response),
                }
            elif state == "PENDING":
                data = {"task_state": "UNKNOWN", "task_id": task_id}
            elif state in ["AWAITING", "STARTED"]:
                data = {"task_state": state, "task_id": task_id}
            elif state == "SUCCESS":
                data = {"task_state": state, "task_id": task_id, "data": result}
            elif state == "STARTED":
                data = {"task_status": state, "task_id": task_id}
            else:
                raise ValueError(f"Unknown task state {state}!")
            return CommonModels.DataResponseModel(data=data)


class CeleryRoute(Route, ABC):
    def __init__(self, app, celery_executor, router=None, async_router=None):
        self.app = app
        self.celery_executor = celery_executor
        self._router = router
        self._async_router = async_router
        self.routed_funcs = []
        self.define_preloads()
        self.define_tasks()
        self.define_routes()

    @property
    def async_router(self):
        return self._async_router or self.app

    @abstractmethod
    def define_tasks(self):
        pass

    def define_preloads(self):
        pass


class CeleryErrorRoute(DefaultErrorRoute):
    DEFAULT_STATUS_CODE_MAPPINGS = {CeleryExecutor.QueueFullException: lambda exc: 429}
    DEFAULT_SILENCED_EXCEPTIONS = {CeleryExecutor.QueueFullException: lambda exc: True}

    def add_default_exceptions_handler(
            fs_app,
            debug=False,
            excs_to_status_codes=None,
            silenced_excs=None,
    ):
        extra_status = {CeleryExecutor.QueueFullException: lambda exc: 429}
        extra_silence = {CeleryExecutor.QueueFullException: lambda exc: True}

        status_codes = {
            **DefaultErrorRoute.DEFAULT_STATUS_CODE_MAPPINGS,
            **(excs_to_status_codes or {}),
            **extra_status,
        }

        silenced = {
            **DefaultErrorRoute.DEFAULT_SILENCED_EXCEPTIONS,
            **(silenced_excs or {}),
            **extra_silence,
        }

        super(CeleryErrorRoute, CeleryErrorRoute).add_default_exceptions_handler(
            fs_app, debug, status_codes, silenced
        )
