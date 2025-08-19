from starlette.requests import Request
from starlette.types import Scope, Receive, Send, ASGIApp

from .handler import ErrorHandler


class ErrorHandlerWrapper:
    """
    在中间件场景包裹下游 ASGI 应用，捕获 HTTP 处理过程中的异常并交由 `ErrorHandler` 转换为响应。

    - 仅在 `http` scope 下工作；其他 scope 直接透传。
    - 推荐在中间件的 `__init__` 中按需启用。

    示例（中间件集成）:
    >>> from typing import Optional
    >>> from starlette.types import ASGIApp
    >>> from ctlib_webstack.fastapi.error_handler import ErrorHandler, ErrorHandlerWrapper
    >>> class SomeMiddleware:
    ...     def __init__(self, app: ASGIApp, *, error_handler: Optional[ErrorHandler] = None) -> None:
    ...         self.app = ErrorHandlerWrapper(app, error_handler) if error_handler else app
    """

    def __init__(
        self,
        app: ASGIApp,
        handler: ErrorHandler,
    ):
        self.app = app
        self.error_handler = handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            response = await self.error_handler(request, exc)
            await response(scope, receive, send)
