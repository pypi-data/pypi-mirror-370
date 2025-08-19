"""Middleware to extract and store request information in context variables."""

from fastapi import FastAPI, Request


def add_request_info_middleware(app: FastAPI) -> None:
    """Add middleware to capture request information like endpoint path and caller-info."""

    @app.middleware("http")
    async def add_request_details_to_logs(request: Request, call_next):
        # Get the current context
        from app.main import request_context

        current_context = request_context.get({})

        # Update the context with the current endpoint path
        current_context["endpoint_path"] = request.url.path

        # Check for X-Caller-Info header and add if present
        if "X-Caller-Info" in request.headers:
            current_context["caller_info"] = request.headers.get("X-Caller-Info")

        # Set the updated context for this request
        request_context.set(current_context)

        # Continue processing the request
        return await call_next(request)
