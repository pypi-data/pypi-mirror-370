import logging
import time

from starlette.types import ASGIApp, Receive, Scope, Send

_access = logging.getLogger("strats.access")


class AccessLogMiddleware:
    def __init__(self, app: ASGIApp, drop_paths=("/healthz", "/livez", "/readyz")):
        self.app = app
        self.drop_paths = set(drop_paths)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        if path in self.drop_paths:
            return await self.app(scope, receive, send)

        method = scope.get("method", "-")
        client = scope.get("client")
        addr = client[0] if client else "-"
        start = time.perf_counter()
        status_holder = {"code": 0}

        async def send_wrapped(message):
            if message["type"] == "http.response.start":
                status_holder["code"] = message.get("status", 0)
            await send(message)

        await self.app(scope, receive, send_wrapped)
        dur_ms = (time.perf_counter() - start) * 1000.0

        _access.info('%s "%s %s" %d %.2fms', addr, method, path, status_holder["code"], dur_ms)
