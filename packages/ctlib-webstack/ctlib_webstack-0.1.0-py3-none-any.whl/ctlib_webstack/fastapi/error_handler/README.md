## ErrorHandler / ErrorHandlerWrapper

统一异常处理设施，兼容按 HTTP 状态码或异常类型注册处理器，提供 before/after 钩子与兜底 500。

### 核心能力

- `ErrorHandler`
  - `add_exception_handler(code_or_exc, handler)`：注册按状态码或异常类型的处理器
  - `add_before_hook(fn)` / `add_after_hook(fn)`：前/后钩子
  - 可直接作为 `app.add_exception_handler(Exception, error_handler)` 的处理器使用
- `ErrorHandlerWrapper`
  - 作为中间件包装，捕获下游所有异常（仅 http scope），交由 `ErrorHandler` 生成响应

### 快速使用

```python
from fastapi import FastAPI
from ctlib_webstack.fastapi.error_handler import ErrorHandler, ErrorHandlerWrapper

app = FastAPI()
error_handler = ErrorHandler(app)

# 作为全局异常处理器（与 Starlette 机制配合）
app.add_exception_handler(Exception, error_handler)

# 或在自定义中间件中包裹下游应用：
class GlobalErrorMiddleware:
    def __init__(self, app):
        self.app = ErrorHandlerWrapper(app, error_handler)

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

app.add_middleware(GlobalErrorMiddleware)
```

### 钩子示例

```python
async def log_before(exc: Exception):
    ...

async def wrap_after(resp):
    # 可返回一个新的 Response 以覆盖
    return resp

error_handler.add_before_hook(log_before)
error_handler.add_after_hook(wrap_after)
```

### 设计要点

- 匹配顺序：`HTTPException.status_code` → 异常类 MRO → 兜底 500
- 兼容异步/同步 handler（同步通过 `run_in_threadpool` 执行）
- 典型用于解决“内层中间件抛异常导致击穿多层中间件”的问题：把错误处理中间件放在最外层


