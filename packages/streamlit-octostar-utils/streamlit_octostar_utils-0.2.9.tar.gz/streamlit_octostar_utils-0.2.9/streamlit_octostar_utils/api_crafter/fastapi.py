import asyncio
from fastapi import Request, Body
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal, Any
from io import BytesIO
import zipfile
from abc import ABC, abstractmethod
import json
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import ast
import uuid
from functools import wraps
import traceback
from copy import copy
import logging

from octostar.client import make_client

MAX_ERROR_MESSAGE_BYTES = 256
MAX_ERROR_TRACEBACK_BYTES = 10240
DEFAULT_PROCESSOR_SUFFIX = "main"


class CommonParsers(object):
    async def parse_form_list(form_data: str, format=Literal["csv", "python"]) -> Optional[List[str]]:
        try:
            if not form_data:
                return None
            if format == "csv":
                return form_data.split(",")
            elif format == "python":
                return ast.literal_eval(form_data)
        except BaseException as e:
            raise ValidationError(f"Parsing failed in parse_from_list: {str(e.__class__)} {str(e)}")


class Route(ABC):
    def route(route, **route_kwargs):
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            func_name = func.__name__
            if asyncio.iscoroutinefunction(func):
                wrapper = async_wrapper
            else:
                wrapper = sync_wrapper
            func_name = func.__name__
            wrapper._route_kwargs = route_kwargs
            wrapper._route_funcname = func_name
            route.routed_funcs.append(wrapper)
            return wrapper

        return decorator

    def include(route):
        def decorator(func):
            func_name = func.__name__
            if getattr(route, func_name, None):
                raise ValueError(f"Cannot have two functions with the same name {func_name} within the same Route!")
            setattr(route, func_name, func)
            return func

        return decorator

    def __init__(self, app, router=None):
        self.app = app
        self._router = router
        self.routed_funcs = []
        self.define_routes()

    @abstractmethod
    def define_routes(self):
        pass

    @property
    def router(self):
        return self._router or self.app

    def include_routes(self, router_mapping=None):
        for func in self.routed_funcs:
            route_kwargs = copy(func._route_kwargs)
            router = self.router
            if route_kwargs.get("router"):
                router = route_kwargs["router"]
            elif router_mapping:
                router = router_mapping.get(func._route_funcname, self.router)
            else:
                router = self.router
            route_kwargs.pop("router", None)
            router.add_api_route(**route_kwargs, endpoint=func)
        return self


class OctostarRoute(Route):
    def __init__(self, app, tasks_routes, celery_executor=None, router=None):
        self.app = app
        self._router = router
        self.routed_funcs = []
        self.tasks_routes = tasks_routes
        self.celery_executor = celery_executor
        self.endpoints = {}
        self.define_routes()

    def register_route(self, op, octostar_task):
        self.endpoints[op.strip("/")] = octostar_task

    def define_routes(self):
        if self.celery_executor:

            @Route.route(self, path="/task-state/{task_id}")
            async def get_task_status(task_id: str) -> JSONResponse:
                task_status = await self.tasks_routes.get_task(task_id, pop=False)
                task_status = task_status.model_dump(mode="json")["data"]["task_state"]
                return JSONResponse(task_status)

            @Route.route(self, path="/task-result/{task_id}")
            async def get_task_result(task_id: str) -> JSONResponse:
                return_data = await self.tasks_routes.get_task(task_id, pop=True)
                return_data = return_data.model_dump(mode="json")["data"]["data"]
                return JSONResponse(return_data)

            @Route.route(self, path="/{op}", methods=["POST"])
            async def send_task(
                op: str,
                os_context: dict = Body(...),
                jwt: str = Body(...),
                params: dict = Body(dict()),
            ) -> str:
                """
                Any request coming from Octostar (e.g. manifest) should enter from here.
                """
                path_params = []
                op = op.split("/")
                if len(op) > 1:
                    path_params = op[1:]
                op = op[0]
                query_params = params
                client = make_client(jwt)
                if op not in self.endpoints.keys():
                    raise StarletteHTTPException(401, f"Route {op} is forbidden for NiFi.")
                task_id = await self.celery_executor.send_task(
                    self.endpoints[op], args=[os_context, client, query_params]
                )
                return task_id

        else:

            @Route.route(self, path="/{op}", methods=["POST"])
            async def call_task(
                op: str,
                os_context: dict = Body(...),
                jwt: str = Body(...),
                params: dict = Body(dict()),
            ) -> str:
                """
                Any request coming from Octostar (e.g. manifest) should enter from here.
                """
                path_params = []
                op = op.split("/")
                if len(op) > 1:
                    path_params = op[1:]
                op = op[0]
                query_params = params
                client = make_client(jwt)
                if op not in self.endpoints.keys():
                    raise StarletteHTTPException(401, f"Route {op} is forbidden for NiFi.")
                result = await self.endpoints[op](os_context, client, query_params)
                return result

    @staticmethod
    def octostar_task(celery_executor, *args, **opts):
        def decorator(func):
            if celery_executor:
                serialized_func = celery_executor.serialized_io(func)
                task_func = celery_executor.app.task(*args, **opts)(serialized_func)
            else:

                @wraps(func)
                def octostar_func(*args, **kwargs):
                    return func(None, *args, **kwargs)

                task_func = octostar_func
            return task_func

        return decorator


class CommonModels(object):
    class OKResponseModel(BaseModel):
        message: str = "OK"
        status: str = "success"

    class DataResponseModel(BaseModel):
        data: Any
        status: str = "success"

    class ZipResponseModel(object):
        class Element(object):
            def __init__(self, file: bytes, path: str, filename: str, json: dict):
                self.file = file
                self.path = path
                self.filename = filename
                self.json = json

        def __init__(
            self,
            elements: List[Element],
            paths: Optional[List[str]] = None,
            filename: Optional[str] = None,
            status: str = "success",
        ):
            self.elements = elements
            self.paths = paths
            self.status = status
            self.filename = filename

        def get(self):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for element in self.elements:
                    file_name = f"{element.path}/{element.filename}"
                    zip_file.writestr(file_name, element.file)
                    json_name = f"{element.path}/{element.filename}.dict"
                    zip_file.writestr(json_name, json.dumps(element.json, indent=4))
                for path in self.paths:
                    zip_file.writestr(path + "/", "")
                zip_file.writestr("response.dict", json.dumps({"status": self.status}, indent=4))
            zip_buffer.seek(0)
            headers = {}
            headers["Content-Disposition"] = "attachment;"
            filename = self.filename or (str(uuid.uuid4()) + ".zip")
            headers["Content-Disposition"] += f' filename="{filename}"'
            return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)


class ErrorLogFilter(logging.Filter):
    def __init__(self, silenced_excs: dict[type, callable]):
        super().__init__()
        self.silenced_excs = silenced_excs

    def _silenced(self, exc_value) -> bool:
        for etype, cond in self.silenced_excs.items():
            if isinstance(exc_value, etype) and cond(exc_value):
                return True
        return False

    def filter(self, record: logging.LogRecord) -> bool:
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            if self._silenced(exc_value):
                return False

        msg = record.getMessage()
        for etype in self.silenced_excs:
            if etype.__name__ in msg:
                if self.silenced_excs[etype](None):
                    return False

        return True


class DefaultErrorRoute:
    DEFAULT_STATUS_CODE_MAPPINGS = {
        StarletteHTTPException: lambda exc: exc.status_code,
        NotImplementedError: lambda exc: 501,
        AssertionError: lambda exc: 400,
        ValidationError: lambda exc: 422,
        RequestValidationError: lambda exc: 422,
    }

    DEFAULT_SILENCED_EXCEPTIONS = {
        RequestValidationError: lambda exc: True,
        ValidationError: lambda exc: True,
        StarletteHTTPException: lambda exc: exc.status_code in [400, 429, 422]
    }

    error_responses = {
        500: {
            "description": "Generic Server Error",
            "content": {
                "application/json": {"example": {"message": "Something unexpected went wrong!", "status": "error"}}
            },
        },
        501: {
            "description": "Not Implemented",
            "content": {
                "application/json": {
                    "example": {"message": "This method (with these parameters) is not implemented!", "status": "error"}
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"message": "These two lists must have the same length!", "status": "error"}
                }
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {"example": {"message": "Validation error on 0 -> filename!", "status": "error"}}
            },
        },
    }

    def format_error(exc, body=b"", debug=False, excs_to_status_codes=DEFAULT_STATUS_CODE_MAPPINGS):
        """Generic Error Handler"""
        status_code = 500
        for exc_type, handler in excs_to_status_codes.items():
            if isinstance(exc, exc_type):
                status_code = handler(exc)
                break
        try:
            message = exc.message
        except:
            message = str(exc)
        if debug:
            message += "\n" + str(body)
        if len(message) > MAX_ERROR_MESSAGE_BYTES:
            message = message[-MAX_ERROR_MESSAGE_BYTES:]
        try:
            tcbk = traceback.format_exception(exc)
            if len(tcbk) > MAX_ERROR_TRACEBACK_BYTES:
                tcbk = tcbk[-MAX_ERROR_TRACEBACK_BYTES:]
        except:
            tcbk = None
        response_content = {"message": message, "status": "error"}
        if debug:
            response_content["traceback"] = tcbk
        return JSONResponse(status_code=status_code, content=response_content)

    async def handle_error(body: bytes, exc: Exception, debug: bool, excs_to_status_codes: dict):
        return DefaultErrorRoute.format_error(exc, body, debug, excs_to_status_codes)

    def add_default_exceptions_handler(
            fs_app,
            debug=False,
            excs_to_status_codes=None,
            silenced_excs=None,
    ):
        if excs_to_status_codes is None:
            excs_to_status_codes = DefaultErrorRoute.DEFAULT_STATUS_CODE_MAPPINGS
        if silenced_excs is None:
            silenced_excs = DefaultErrorRoute.DEFAULT_SILENCED_EXCEPTIONS

        async def _async_handle_error(request: Request, exc: Exception):
            return await DefaultErrorRoute.handle_error(b"", exc, debug, excs_to_status_codes)

        # Added all three since FastAPI seems to intercept some exceptions before Exception
        fs_app.add_exception_handler(RequestValidationError, _async_handle_error)
        fs_app.add_exception_handler(StarletteHTTPException, _async_handle_error)
        fs_app.add_exception_handler(Exception, _async_handle_error)

        log_filter = ErrorLogFilter(silenced_excs)
        for name in ("uvicorn.error", "uvicorn.access", "fastapi", "uvicorn"):
            logging.getLogger(name).addFilter(log_filter)

        logging.getLogger().addFilter(log_filter)

class RequestCancelledMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        queue = asyncio.Queue()

        async def message_poller(sentinel, handler_task):
            nonlocal queue
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    handler_task.cancel()
                    return sentinel
                await queue.put(message)

        sentinel = object()
        handler_task = asyncio.create_task(self.app(scope, queue.get, send))
        asyncio.create_task(message_poller(sentinel, handler_task))
        try:
            return await handler_task
        except asyncio.CancelledError:
            print("Cancelling request due to disconnect")
