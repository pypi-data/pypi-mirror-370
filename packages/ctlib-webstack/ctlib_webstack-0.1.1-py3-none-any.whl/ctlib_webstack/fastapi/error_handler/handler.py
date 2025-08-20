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

AfterHook = Callable[[Request, Response, Exception], Awaitable[Optional[Response]]]
BeforeHook = Callable[[Request, Exception], Awaitable[None]]

_UNHANDLED_FLAG_ATTR = "_ctlib_error_handler_unhandled"


async def default_final_handler(request: Request, exc: Exception) -> Response:  # noqa: F841
    logger.exception(exc)
    return Response("Internal Server Error", status_code=500)


class ErrorHandler:
    def __init__(
        self,
        app: Optional[Starlette] = None,
        before_hooks: Optional[List[BeforeHook]] = None,
        after_hooks: Optional[List[AfterHook]] = None,
        final_handler: Optional[ExceptionHandler] = default_final_handler,
    ):
        self.status_handlers: Dict[int, ExceptionHandler] = {}
        self.exception_handlers: Dict[Any, ExceptionHandler] = {}
        self.final_exception_handler = final_handler
        self.before_hooks = before_hooks or []
        self.after_hooks = after_hooks or []

        if app:
            for key, value in app.exception_handlers.items():  # noqa: F401
                self.add_exception_handler(key, value)

    def add_before_hook(self, fn: BeforeHook) -> BeforeHook:
        self.before_hooks.append(fn)
        return fn

    def add_after_hook(self, fn: AfterHook) -> AfterHook:
        self.after_hooks.append(fn)
        return fn

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

    def set_final_handler(self, handler: ExceptionHandler) -> None:
        self.final_exception_handler = handler

    def before_hook(self, func: BeforeHook) -> BeforeHook:
        self.before_hooks.append(func)
        return func

    def after_hook(self, func: AfterHook) -> AfterHook:
        self.after_hooks.append(func)
        return func

    async def __call__(self, request: Request, exc: Exception) -> Response:
        for fn in self.before_hooks:
            await fn(request, exc)

        handler = self.lookup_exception_handler(exc)

        if handler is None:
            try:
                setattr(exc, _UNHANDLED_FLAG_ATTR, True)
            except Exception:
                pass
            raise exc

        if asyncio.iscoroutinefunction(handler):
            response = await handler(request, exc)
        else:
            response = await run_in_threadpool(handler, request, exc)

        if response is None:
            # handler 未进行处理
            try:
                setattr(exc, _UNHANDLED_FLAG_ATTR, True)
            except Exception:
                pass
            raise exc

        for fn in self.after_hooks:
            if resp := await fn(request, response, exc):
                response = resp

        return response


class ErrorHandlerChain:
    def __init__(self, *handlers: ErrorHandler):
        self.handlers = handlers

    async def __call__(self, request: Request, exc: Exception) -> Response:
        for handler in self.handlers:
            try:
                resp = await handler(request, exc)
                if resp:
                    return resp
            except Exception as new_exc:
                if getattr(new_exc, _UNHANDLED_FLAG_ATTR, False):
                    continue
                logger.warning(f"ErrorHandler raised new exception: {new_exc}", exc_info=new_exc)
        raise exc
