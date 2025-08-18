import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from helpr.logging import Logger

class LoggingContextMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app,custom_logger:Logger, service: str = "unknown", env: str = "dev"):
        super().__init__(app)
        self.service = service
        self.env = env
        self.custom_logger = custom_logger
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        request_id = str(uuid.uuid4())

        user_id = getattr(request.state, "user_id", None)
        if user_id:
            self.custom_logger.set_log_context(user_id=user_id)
        session_id=request.headers.get("X-CLY-SESSION-IDENTIFIER", "")
        if session_id:
            self.custom_logger.set_log_context(session_id=session_id)
        self.custom_logger.set_log_context(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            service=self.service,
            env=self.env
        )

        try:
            response: Response = await call_next(request)
            return response
        finally:
            latency_ms = int((time.perf_counter() - start) * 1000)
            self.custom_logger.set_log_context(latency_ms=latency_ms)
            self.custom_logger.info(f"Latency in request: {latency_ms} ms", )
            self.custom_logger.clear_log_context()