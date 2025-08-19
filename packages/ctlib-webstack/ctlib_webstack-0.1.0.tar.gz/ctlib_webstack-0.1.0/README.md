## ctlib-webstack

面向 FastAPI/Starlette 的 Web 组件集合，目前包含：

- IP 访问地理过滤中间件（`IPFilterMiddleware`）
- 统一错误处理器与中间件包装（`ErrorHandler` / `ErrorHandlerWrapper`）

### 特性

- 按国家/地区/城市或地理编码的灵活过滤规则
- 统一异常分派：按 HTTP 状态码或异常类型注册处理器，未命中回退 500
- 支持异常处理前/后钩子，方便埋点、告警、统一响应格式化
- 中间件级一键包裹，兜住下游所有异常，避免“内层中间件异常击穿”

### 目录结构

- `src/ctlib_webstack/fastapi/ip_filter/`：IP 地理过滤中间件
- `src/ctlib_webstack/fastapi/error_handler/`：统一错误处理

### 快速上手（FastAPI）

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
    error_handler=error_handler,  # 可选：启用统一异常处理
)
```

### 过滤规则说明（示例）

- `GeoCode:<code>`：地理编码，如 `GeoCode:HK-HCW---`
- `GeoID:<int>`：地理 ID，如 `GeoID:12345`
- `Geo:<name>`：名称匹配，如 `Geo:Shenzhen`
- `country-region-city`：分段（可截断），如 `US-Texas`、`CN`、`HK-Yau Tsim Mong`

数据来源参考 `ctlib_geoip` 项目。

### 开发提示

- 本仓库使用 `src/` 布局；在本地直接运行示例时，可将项目根目录加入 `PYTHONPATH` 或以可编辑模式安装本项目。

### 相关文档

- `src/ctlib_webstack/fastapi/ip_filter/README.md`
- `src/ctlib_webstack/fastapi/error_handler/README.md`


