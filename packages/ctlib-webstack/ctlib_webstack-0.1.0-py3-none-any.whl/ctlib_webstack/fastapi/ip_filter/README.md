## IPFilterMiddleware

基于客户端 IP 地理位置进行访问控制的 FastAPI/Starlette 中间件。

### 安装

确保已安装并可访问 `ctlib_geoip` 所依赖的数据源服务。

### 使用示例

```python
from fastapi import FastAPI
from ctlib_webstack.fastapi import IPFilterMiddleware, ErrorHandler

app = FastAPI()

error_handler = ErrorHandler(app)

app.add_middleware(
    IPFilterMiddleware,
    ip_info_url="https://your-geoip-endpoint",
    filter_regions=[
        "Geo:Shenzhen",
        "GeoCode:HK-HCW---",
        "US-Texas",
    ],
    error_handler=error_handler,  # 可选：统一异常处理
)
```

### 参数

- `ip_info_url: str`：GeoIP 查询服务端点，传入 `AsyncGeoIPClient`
- `filter_regions: List[str]`：待拦截地区表达式
- `bypass_func(request) -> bool`：返回 True 时跳过过滤
- `before_filter_func(request) -> Optional[Response]`：过滤前回调
- `after_filter_func(request) -> Optional[Response]`：过滤后回调（未命中时）
- `filter_response(request) -> Response`：命中拦截时的响应（默认 503）
- `error_handler: ErrorHandler`（可选）：启用统一异常处理

### 规则格式

- `GeoCode:<code>`：如 `GeoCode:HK-HCW---`
- `GeoID:<int>`：如 `GeoID:12345`
- `Geo:<name>`：如 `Geo:Shenzhen`
- `country-region-city`（可截断）：如 `US-Texas`、`CN`、`HK-Yau Tsim Mong`

### 处理流程

1. 非 http scope 直接放行
2. 执行 `bypass_func` → True 放行
3. 执行 `before_filter_func` → 若返回响应则直接返回
4. 查询 `AsyncGeoIPClient.lookup(ip)` 获得 `GeoInfo`
5. 若 `geo_tree.contains(geoip)` → 返回 `filter_response`
6. 执行 `after_filter_func` → 若返回响应则直接返回
7. 放行下游应用


