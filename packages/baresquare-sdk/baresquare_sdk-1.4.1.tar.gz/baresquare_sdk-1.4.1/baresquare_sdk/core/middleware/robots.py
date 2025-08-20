from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


class RobotsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response


def add_robots_middleware(app: FastAPI) -> None:
    """Add robots middleware to FastAPI app.

    Prevents search engines from indexing the application.
    """
    app.add_middleware(RobotsMiddleware)
