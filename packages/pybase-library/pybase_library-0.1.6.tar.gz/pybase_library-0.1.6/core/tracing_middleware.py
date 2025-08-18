from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from contextvars import ContextVar

request_id_var = ContextVar("request_id", default=None)


# Helper function để lấy trace ID hiện tại
def get_trace_id():
    trace_id = request_id_var.get()
    if trace_id is None:
        trace_id = str(uuid.uuid4())
        request_id_var.set(trace_id)
    return trace_id


class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Tạo trace ID mới cho mỗi request
        trace_id = str(uuid.uuid4())
        request_id_var.set(trace_id)

        # Thêm trace ID vào header response
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id

        return response
