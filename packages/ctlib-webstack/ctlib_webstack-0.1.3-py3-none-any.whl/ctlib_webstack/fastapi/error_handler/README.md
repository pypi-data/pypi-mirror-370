## ErrorHandler / ErrorHandlerMiddleware / ErrorHandlerWrapper

统一异常处理设施，兼容按 HTTP 状态码或异常类型注册处理器，提供 before/after 钩子（支持装饰器注册）。

### 核心能力

- `ErrorHandler`
  - `add_exception_handler(code_or_exc, handler)`：注册按状态码或异常类型的处理器
  - `add_before_hook(fn)` / `add_after_hook(fn)`：前/后钩子
  - `before_hook()` / `after_hook()`：装饰器形式注册前/后钩子
  - 可直接作为 `app.add_exception_handler(Exception, error_handler)` 的处理器使用
- `ErrorHandlerMiddleware`
  - 作为中间件包装，捕获下游所有异常（仅 http scope），交由 `ErrorHandler` 生成响应
- `ErrorHandlerWrapper`
  - 实现即为中间件，可作为“包装器”或“中间件”两种形态使用；与 `ErrorHandlerMiddleware` 为同一实现，命名仅为语义更清晰

### 快速使用

```python
from fastapi import FastAPI
from ctlib_webstack.fastapi.error_handler import (
    ErrorHandler,
    ErrorHandlerMiddleware,  # 推荐
    ErrorHandlerWrapper,  # 同实现命名，亦可直接使用
)

app = FastAPI()

# 可不传 app，按需后续再绑定到 FastAPI（异常仍可被捕获并处理）
error_handler = ErrorHandler()

# 作为全局异常处理器（与 Starlette 机制配合）
app.add_exception_handler(Exception, error_handler)

# 在自定义中间件中包裹下游应用：
class GlobalErrorMiddleware:
    def __init__(self, app):
        self.app = ErrorHandlerWrapper(app, error_handler)

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

app.add_middleware(GlobalErrorMiddleware)
```

### 钩子示例

```python
# 装饰器注册（推荐，无括号用法）
@error_handler.before_hook
async def before_with_ctx(request, exc):
    ...

@error_handler.after_hook
async def after_with_ctx(request, response, exc):
    # 可返回一个新的 Response 覆盖，也可返回 None 表示不变
    return None


# 或使用方法注册（等价）
error_handler.add_before_hook(before_with_ctx)
error_handler.add_after_hook(after_with_ctx)
```

### 设计要点

- 匹配顺序：`HTTPException.status_code` → 异常类 MRO → 兜底 500
- 兼容异步/同步 handler（同步通过 `run_in_threadpool` 执行）
- 典型用于解决“内层中间件抛异常导致击穿多层中间件”的问题：把错误处理中间件放在最外层

### 变更说明（与历史版本兼容性）

- 新增 `ErrorHandlerMiddleware` 以增强语义清晰度；其与 `ErrorHandlerWrapper` 为同一实现（两者均为中间件实现，`Wrapper` 既可作为包装器也可作为中间件使用）
- `ErrorHandler.__init__` 支持可选参数：`app`、`before_hooks`、`after_hooks`、`final_handler`
- `add_after_hook` 的类型签名为 `Awaitable[Optional[Response]]`
- 仅当传入 `app` 时才复制其 `exception_handlers`

#### 新增 API 与行为
- `set_final_handler(handler)`：显式设置兜底处理器。
- Hook 签名统一：
  - before: `fn(request, exc)`
  - after: `fn(request, response, exc)`
- 通过在原始异常对象上设置特定属性以标识“未处理”，`ErrorHandlerChain` 基于该标识继续向后尝试，不改变异常类型。


