from fastapi.middleware.gzip import GZipMiddleware


def add_compression_middleware(app):
    """Add GZIP compression middleware to FastAPI app.

    Compresses responses larger than 1KB to reduce bandwidth usage.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(GZipMiddleware, minimum_size=1000)
