from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(
    app,
    allow_origins=None,
    allow_credentials=True,
    allow_methods=None,
    allow_headers=None,
    max_age=86400,
):
    """Add CORS middleware to FastAPI app.

    Provides permissive defaults suitable for development or internal services.

    Args:
        app: FastAPI application instance
        allow_origins: List of allowed origins. Defaults to ["*"] (all origins)
        allow_credentials: Whether to allow credentials. Defaults to True
        allow_methods: List of allowed HTTP methods. Defaults to ["*"] (all methods)
        allow_headers: List of allowed headers. Defaults to ["*"] (all headers)
        max_age: Cache duration for preflight requests in seconds. Defaults to 86400 (24 hours)

    Note:
        Default settings are very permissive. Consider restricting origins, methods,
        and headers in production environments.
    """
    if allow_origins is None:
        allow_origins = ["*"]
    if allow_methods is None:
        allow_methods = ["*"]
    if allow_headers is None:
        allow_headers = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        max_age=max_age,
    )
