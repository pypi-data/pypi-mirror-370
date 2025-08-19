import asyncio
import logging
from typing import Dict, Any, Union, Type, Optional, Callable, Awaitable, List

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ExceptionHandler

logger = logging.getLogger("ctlib_webstack.fastapi.error_handler")


async def internal_server_error_handler(request: Request, exc: Exception) -> Response:  # noqa: F841
    logger.exception(exc)
    return Response("Internal Server Error", status_code=500)


class ErrorHandler:
    def __init__(
        self,
        app: Starlette,
        before_hooks: List[Callable[[Exception], Awaitable[None]]] = None,
        after_hooks: List[Callable[[Response], Optional[Awaitable[Response]]]] = None,
        final_exception_handler: Callable[[Request, Exception], Awaitable[Response]] = internal_server_error_handler
    ):
        self.status_handlers: Dict[int, ExceptionHandler] = {}
        self.exception_handlers: Dict[Any, ExceptionHandler] = {}
        self.final_exception_handler = final_exception_handler
        self.before_hooks = before_hooks or []
        self.after_hooks = after_hooks or []

        for key, value in app.exception_handlers.items():  # noqa: F401
            self.add_exception_handler(key, value)

    def add_before_hook(self, fn: Callable[[Exception], Awaitable[None]]):
        self.before_hooks.append(fn)

    def add_after_hook(self, fn: Callable[[Response], Optional[Awaitable[Response]]]):
        self.after_hooks.append(fn)

    @staticmethod
    def _lookup_exception_handler(exc_handlers: Dict[Any, ExceptionHandler], exc: Exception) -> Optional[ExceptionHandler]:
        for cls in type(exc).__mro__:
            if cls in exc_handlers:
                return exc_handlers[cls]
        return None

    def lookup_exception_handler(self, exc: Exception) -> Optional[ExceptionHandler]:
        handler = None

        if isinstance(exc, HTTPException):
            handler = self.status_handlers.get(exc.status_code)

        if handler is None:
            handler = self._lookup_exception_handler(self.exception_handlers, exc)

        if handler is None:
            handler = self.final_exception_handler

        return handler

    def add_exception_handler(
        self,
        exc_class_or_status_code: Union[int, Type[Exception]],
        handler: ExceptionHandler,
    ) -> None:
        if exc_class_or_status_code in (500, Exception):
            self.final_exception_handler = handler
            return

        if isinstance(exc_class_or_status_code, int):
            self.status_handlers[exc_class_or_status_code] = handler
        else:
            assert issubclass(exc_class_or_status_code, Exception)
            self.exception_handlers[exc_class_or_status_code] = handler

    def exception_handler(
        self,
        exc_class_or_status_code: Union[int, Type[Exception]],
    ) -> Callable[[ExceptionHandler], ExceptionHandler]:
        def decorator(func: ExceptionHandler) -> ExceptionHandler:
            self.add_exception_handler(exc_class_or_status_code, func)
            return func

        return decorator

    async def __call__(self, request: Request, exc: Exception) -> Response:
        for fn in self.before_hooks:
            await fn(exc)

        handler = self.lookup_exception_handler(exc)

        if handler is None:
            raise exc

        if asyncio.iscoroutinefunction(handler):
            response = await handler(request, exc)
        else:
            response = await run_in_threadpool(handler, request, exc)

        for fn in self.after_hooks:
            if resp := await fn(response):
                response = resp

        return response
