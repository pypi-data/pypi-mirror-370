import logging
from typing import List, Callable, Awaitable, Optional

from ctlib_geoip import AsyncGeoIPClient, GeoTree, GeoInfo
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Scope, Receive, Send

from ctlib_webstack.fastapi.error_handler import ErrorHandler, ErrorHandlerWrapper

logger = logging.getLogger("ctlib_webstack.fastapi.ip_filter")


async def default_bypass_func(_: Request) -> bool:
    return False


async def default_filter_response(_: Request) -> Response:
    return Response("Service Unavailable", status_code=503)


async def return_none(_: Request) -> None:
    return None


def geo_filter_tree(filter_regions: List[str]) -> GeoTree:
    """
    根据给定的地区表达式构建用于“拦截”的 GeoTree。

    参数:
    数据源: https://git.codetech.top/ctlib/ctlib-geoip/src/branch/master/src/ctlib_geoip/data
    - filter_regions: 字符串列表；每个元素描述一个需拦截的地理位置。支持以下格式（命中则视为“禁止访问”）：
      - "GeoCode:<code>": 使用地理编码（示例: "GeoCode:HK-HCW---" 表示香港中西区）
      - "GeoID:<int>": 使用地理 ID（示例: "GeoID:12345"）
      - "Geo:<name>": 使用名称查找（示例: "Geo:Shenzhen", "Geo:Hangzhou"）
      - "country-region-city": 以“-”分隔，可截断（示例: "US-Texas", "US-Florida", "HK-Yau Tsim Mong", "CN"）

    返回:
    - GeoTree: 包含所有需拦截地区的匹配树，可用于 GeoIP 判断（tree.contains(geoip) 为 True 即命中拦截）。

    示例:
    >>> from ctlib_geoip import GeoTree, GeoInfo, GeoIP
    >>> blocked = geo_filter_tree([
    ...     "Geo:Shenzhen",
    ...     "GeoCode:HK-HCW---",
    ...     "US-Texas",
    ... ])
    >>> geoip = GeoIP(ip="1.2.3.4", country="US", region="Texas", city="Houston")
    >>> if blocked.contains(geoip):
    ...     # 命中拦截
    ...     ...
    """
    geo_tree = GeoTree()
    for region in filter_regions:
        try:
            if region.startswith("GeoCode:"):
                geo_tree.add(GeoInfo.from_geo_code(region[8:]))
            elif region.startswith("GeoID:"):
                geo_tree.add(GeoInfo.from_geo_id(int(region[6:])))
            elif region.startswith("Geo:"):
                geo_tree.add(GeoInfo.from_name(region[4:]))
            else:
                _country = _region = _city = None
                res = region.split("-")
                if len(res) == 1:
                    _country = res[0]
                elif len(res) == 2:
                    _country, _region = res
                elif len(res) >= 3:
                    _country, _region, _city, *_ = res
                geo_tree.add(GeoInfo(country=_country, region=_region, city=_city))
        except Exception as e:
            logger.exception(e)
    return geo_tree


class IPFilterMiddleware:
    """
    基于客户端 IP 地理位置进行访问控制的 FastAPI/Starlette 中间件。
    当请求来源地命中 `filter_regions` 描述的地区集合时，将返回 `filter_response`（默认 503）。

    参数:
    - app: 下游 ASGI 应用。
    - ip_info_url: GeoIP 查询服务端点，将传入 `AsyncGeoIPClient` 用于 `lookup(ip)`。
    - filter_regions: 字符串列表，描述需拦截（禁止访问）的地区，支持以下格式：
      - "GeoCode:<code>": 使用地理编码（示例: "GeoCode:HK-HCW---" 表示香港中西区）
      - "GeoID:<int>": 使用地理 ID（示例: "GeoID:12345"）
      - "Geo:<name>": 使用名称查找（示例: "Geo:Shenzhen", "Geo:Hangzhou"）
      - "country-region-city": 以“-”分隔，可截断（示例: "US-Texas", "US-Florida", "HK-Yau Tsim Mong", "CN"）
      数据源: https://git.codetech.top/ctlib/ctlib-geoip/src/branch/master/src/ctlib_geoip/data
    - bypass_func: 异步函数，返回 True 则跳过过滤（例如健康检查路径、内网来源）。
    - before_filter_func: 异步函数，过滤前回调；若返回 `Response` 将直接返回。
    - after_filter_func: 异步函数，过滤后回调（未命中拦截时执行）；若返回 `Response` 将直接返回。
    - filter_response: 异步函数，命中拦截时返回的响应，默认返回 503。
    - error_handler: 可选的 `ErrorHandler`。若提供，则使用 `ErrorHandlerWrapper(app, error_handler)` 包裹下游应用，
      以便在中间件链路内统一捕获和处理异常。

    处理流程:
    1) 非 http scope 直接放行；
    2) 执行 `bypass_func`，返回 True 则放行；
    3) 执行 `before_filter_func`，若返回响应则直接返回；
    4) 通过 `AsyncGeoIPClient.lookup(request.client.host)` 获取 `GeoInfo`；
    5) 若 `geo_tree.contains(geoip)` 为 True，则返回 `filter_response`；
    6) 否则执行 `after_filter_func`，若返回响应则直接返回；
    7) 最终放行给下游应用。

    使用示例:
    >>> from fastapi import FastAPI
    >>> from ctlib_webstack.fastapi import IPFilterMiddleware, ErrorHandler
    >>> app = FastAPI()
    >>> error_handler = ErrorHandler(app)
    >>> app.add_middleware(
    ...     IPFilterMiddleware,
    ...     ip_info_url="https://your-geoip-endpoint",
    ...     filter_regions=[
    ...         "Geo:Shenzhen",
    ...         "GeoCode:HK-HCW---",
    ...         "US-Texas",
    ...     ],
    ...     error_handler=error_handler,
    ... )
    """

    def __init__(
        self,
        app: ASGIApp, *,
        ip_info_url: str = None,
        filter_regions: List[str] = None,
        bypass_func: Callable[[Request], Awaitable[bool]] = default_bypass_func,
        before_filter_func: Callable[[Request], Awaitable[Optional[Response]]] = return_none,
        after_filter_func: Callable[[Request], Awaitable[Optional[Response]]] = return_none,
        filter_response: Callable[[Request], Awaitable[Response]] = default_filter_response,
        error_handler: Optional[ErrorHandler] = None
    ) -> None:
        if error_handler:
            self.app = ErrorHandlerWrapper(app, error_handler)
        else:
            self.app = app
        self.geo_client = AsyncGeoIPClient(ip_info_url)
        self.geo_tree = geo_filter_tree(filter_regions)
        self.bypass_func = bypass_func
        self.before_filter_func = before_filter_func
        self.after_filter_func = after_filter_func
        self.filter_response_func = filter_response

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # pragma: no cover
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        if await self.bypass_func(request):
            await self.app(scope, receive, send)
            return

        if response := await self.before_filter_func(request):
            await response(scope, receive, send)
            return

        ip = request.client.host
        geoip = await self.geo_client.lookup(ip)
        if not geoip:
            logger.warning(f"geoip lookup failed for {ip}")
        if geoip and self.geo_tree.contains(geoip):
            response = await self.filter_response_func(request)
            await response(scope, receive, send)
            return

        if response := await self.after_filter_func(request):
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
