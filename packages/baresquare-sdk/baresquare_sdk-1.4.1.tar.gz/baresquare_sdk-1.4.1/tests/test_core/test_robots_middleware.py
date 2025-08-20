from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from baresquare_sdk.core.middleware.robots import RobotsMiddleware, add_robots_middleware


class TestRobotsMiddleware:
    """Test cases for RobotsMiddleware class."""

    @pytest.mark.asyncio
    async def test_dispatch__adds_robots_header(self):
        """Test that dispatch adds the correct X-Robots-Tag header."""
        # Arrange
        app = FastAPI()
        middleware = RobotsMiddleware(app)
        mock_request = MagicMock(spec=Request)
        mock_response = Response(content="test")
        mock_call_next = AsyncMock(return_value=mock_response)

        # Act
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert result.headers["X-Robots-Tag"] == "noindex, nofollow"
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch__preserves_existing_headers(self):
        """Test that dispatch preserves existing response headers."""
        # Arrange
        app = FastAPI()
        middleware = RobotsMiddleware(app)
        mock_request = MagicMock(spec=Request)
        mock_response = Response(content="test")
        mock_response.headers["Content-Type"] = "application/json"
        mock_call_next = AsyncMock(return_value=mock_response)

        # Act
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert result.headers["X-Robots-Tag"] == "noindex, nofollow"
        assert result.headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_dispatch__overwrites_existing_robots_header(self):
        """Test that dispatch overwrites existing X-Robots-Tag header."""
        # Arrange
        app = FastAPI()
        middleware = RobotsMiddleware(app)
        mock_request = MagicMock(spec=Request)
        mock_response = Response(content="test")
        mock_response.headers["X-Robots-Tag"] = "index, follow"
        mock_call_next = AsyncMock(return_value=mock_response)

        # Act
        result = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert result.headers["X-Robots-Tag"] == "noindex, nofollow"


class TestAddRobotsMiddleware:
    """Test cases for add_robots_middleware function."""

    def test_add_robots_middleware__adds_middleware_to_app(self):
        """Test that add_robots_middleware adds the middleware to the FastAPI app."""
        # Arrange
        app = FastAPI()

        # Act
        add_robots_middleware(app)

        # Assert
        # Check that the middleware was added by looking for RobotsMiddleware in the middleware stack
        middleware_classes = [middleware.cls for middleware in app.user_middleware]
        assert RobotsMiddleware in middleware_classes

    def test_add_robots_middleware__preserves_existing_middleware(self):
        """Test that add_robots_middleware preserves existing middleware."""
        # Arrange
        app = FastAPI()
        initial_middleware_count = len(app.user_middleware)

        # Act
        add_robots_middleware(app)

        # Assert
        assert len(app.user_middleware) == initial_middleware_count + 1
        middleware_classes = [middleware.cls for middleware in app.user_middleware]
        assert RobotsMiddleware in middleware_classes
