"""Tests for Authentication functionality using mocking."""

import os
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes

from baresquare_sdk.aws.authentication import (
    UnauthenticatedException,
    UnauthorizedException,
    VerifyToken,
    generate_auth0_token,
    is_jwt_expired,
    obtain_auth0_token,
)


class TestVerifyToken:
    """Test suite for VerifyToken class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.verify_token = VerifyToken()
        self.mock_token = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InRlc3Qta2lkIn0"
        )
        self.mock_request = MagicMock(spec=Request)
        self.mock_request.state = MagicMock()

    def test_verify_token_initialization(self):
        """Test VerifyToken initializes with None jwks_client."""
        verify_token = VerifyToken()
        assert verify_token.jwks_client is None

    @patch("baresquare_sdk.aws.authentication.jwt.PyJWKClient")
    @patch.dict(
        os.environ,
        {
            "AUTH0_DOMAIN": "test-domain.auth0.com",
            "PL_ENV": "test",
            "PL_SERVICE": "test-service",
            "PL_REGION": "us-east-1",
        },
        clear=True,
    )
    def test_initialize_client(self, mock_pyjwk_client):
        """Test JWKS client initialization."""
        # Arrange
        mock_client = MagicMock()
        mock_pyjwk_client.return_value = mock_client

        # Act
        self.verify_token.initialize_client()

        # Assert
        mock_pyjwk_client.assert_called_once_with("https://test-domain.auth0.com/.well-known/jwks.json")
        assert self.verify_token.jwks_client == mock_client

    @pytest.mark.asyncio
    async def test_verify_no_token_raises_unauthenticated(self):
        """Test that missing token raises UnauthenticatedException."""
        with pytest.raises(UnauthenticatedException):
            await self.verify_token.verify(security_scopes=SecurityScopes(), token=None, request=self.mock_request)

    @pytest.mark.asyncio
    @patch("baresquare_sdk.aws.authentication.jwt.decode")
    @patch("baresquare_sdk.aws.authentication.jwt.PyJWKClient")
    @patch.dict(
        os.environ,
        {
            "AUTH0_DOMAIN": "test-domain.auth0.com",
            "AUTH0_API_AUDIENCE": "test-audience",
            "PL_ENV": "test",
            "PL_SERVICE": "test-service",
            "PL_REGION": "us-east-1",
        },
        clear=True,
    )
    async def test_verify_success(self, mock_pyjwk_client, mock_jwt_decode):
        """Test successful token verification."""
        # Arrange
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test-key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_pyjwk_client.return_value = mock_client

        expected_payload = {"sub": "user123", "aud": "test-audience"}
        mock_jwt_decode.return_value = expected_payload

        # Act
        result = await self.verify_token.verify(
            security_scopes=SecurityScopes(), token=self.mock_token, request=self.mock_request
        )

        # Assert
        assert result == expected_payload
        mock_client.get_signing_key_from_jwt.assert_called_once_with(self.mock_token.credentials)
        mock_jwt_decode.assert_called_once_with(
            self.mock_token.credentials,
            "test-key",
            algorithms="RS256",
            audience="test-audience",
            issuer="https://test-domain.auth0.com/",
        )
        # Check that payload is stored in request state
        assert self.mock_request.state.auth_payload == expected_payload

    @pytest.mark.asyncio
    @patch("baresquare_sdk.aws.authentication.jwt.PyJWKClient")
    @patch.dict(
        os.environ,
        {
            "AUTH0_DOMAIN": "test-domain.auth0.com",
            "PL_ENV": "test",
            "PL_SERVICE": "test-service",
            "PL_REGION": "us-east-1",
        },
        clear=True,
    )
    async def test_verify_jwks_client_error(self, mock_pyjwk_client):
        """Test verification failure due to JWKS client error."""
        # Arrange
        mock_client = MagicMock()
        mock_client.get_signing_key_from_jwt.side_effect = jwt.exceptions.PyJWKClientError("Invalid key")
        mock_pyjwk_client.return_value = mock_client

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await self.verify_token.verify(
                security_scopes=SecurityScopes(), token=self.mock_token, request=self.mock_request
            )

        assert "Invalid key" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("baresquare_sdk.aws.authentication.jwt.PyJWKClient")
    @patch.dict(
        os.environ,
        {
            "AUTH0_DOMAIN": "test-domain.auth0.com",
            "PL_ENV": "test",
            "PL_SERVICE": "test-service",
            "PL_REGION": "us-east-1",
        },
        clear=True,
    )
    async def test_verify_decode_error(self, mock_pyjwk_client):
        """Test verification failure due to JWT decode error."""
        # Arrange
        mock_client = MagicMock()
        mock_client.get_signing_key_from_jwt.side_effect = jwt.exceptions.DecodeError("Invalid token")
        mock_pyjwk_client.return_value = mock_client

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await self.verify_token.verify(
                security_scopes=SecurityScopes(), token=self.mock_token, request=self.mock_request
            )

        assert "Invalid token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("baresquare_sdk.aws.authentication.jwt.decode")
    @patch("baresquare_sdk.aws.authentication.jwt.PyJWKClient")
    @patch.dict(
        os.environ,
        {
            "AUTH0_DOMAIN": "test-domain.auth0.com",
            "AUTH0_API_AUDIENCE": "test-audience",
            "PL_ENV": "test",
            "PL_SERVICE": "test-service",
            "PL_REGION": "us-east-1",
        },
        clear=True,
    )
    async def test_verify_jwt_validation_error(self, mock_pyjwk_client, mock_jwt_decode):
        """Test verification failure due to JWT validation error."""
        # Arrange
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test-key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_pyjwk_client.return_value = mock_client

        mock_jwt_decode.side_effect = jwt.exceptions.ExpiredSignatureError("Token expired")

        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await self.verify_token.verify(
                security_scopes=SecurityScopes(), token=self.mock_token, request=self.mock_request
            )

        assert "Token expired" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("baresquare_sdk.aws.authentication.jwt.decode")
    @patch("baresquare_sdk.aws.authentication.jwt.PyJWKClient")
    @patch.dict(
        os.environ,
        {
            "AUTH0_DOMAIN": "test-domain.auth0.com",
            "AUTH0_API_AUDIENCE": "test-audience",
            "PL_ENV": "test",
            "PL_SERVICE": "test-service",
            "PL_REGION": "us-east-1",
        },
        clear=True,
    )
    async def test_verify_without_request(self, mock_pyjwk_client, mock_jwt_decode):
        """Test verification without request object (no state storage)."""
        # Arrange
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test-key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_pyjwk_client.return_value = mock_client

        expected_payload = {"sub": "user123"}
        mock_jwt_decode.return_value = expected_payload

        # Act
        result = await self.verify_token.verify(security_scopes=SecurityScopes(), token=self.mock_token, request=None)

        # Assert
        assert result == expected_payload
        # Should not crash when request is None


class TestGenerateAuth0Token:
    """Test suite for generate_auth0_token function."""

    @patch("baresquare_sdk.aws.authentication.requests.post")
    def test_generate_auth0_token_success(self, mock_post):
        """Test successful Auth0 token generation."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test-token-123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Act
        result = generate_auth0_token("test-domain.auth0.com", "test-client-id", "test-client-secret", "test-audience")

        # Assert
        assert result == "test-token-123"
        mock_post.assert_called_once_with(
            "https://test-domain.auth0.com/oauth/token",
            data={
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "audience": "test-audience",
                "grant_type": "client_credentials",
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        mock_response.raise_for_status.assert_called_once()

    @patch("baresquare_sdk.aws.authentication.requests.post")
    def test_generate_auth0_token_http_error(self, mock_post):
        """Test Auth0 token generation with HTTP error."""
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 401 Unauthorized")
        mock_post.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            generate_auth0_token("test-domain.auth0.com", "test-client-id", "test-client-secret", "test-audience")

        assert "HTTP 401 Unauthorized" in str(exc_info.value)


class TestIsJWTExpired:
    """Test suite for is_jwt_expired function."""

    @patch("baresquare_sdk.aws.authentication.jwt.get_unverified_header")
    @patch("baresquare_sdk.aws.authentication.jwt.decode")
    @patch("baresquare_sdk.aws.authentication.time.time")
    def test_is_jwt_expired_true(self, mock_time, mock_jwt_decode, mock_get_header):
        """Test JWT token that is expired."""
        # Arrange
        mock_get_header.return_value = {"alg": "RS256"}
        mock_jwt_decode.return_value = {"exp": 1000000}  # Past timestamp
        mock_time.return_value = 2000000  # Current timestamp

        # Act
        result = is_jwt_expired("test-token")

        # Assert
        assert result is True
        mock_get_header.assert_called_once_with(jwt="test-token")
        mock_jwt_decode.assert_called_once_with(
            jwt="test-token", algorithms=["RS256"], options={"verify_signature": False}
        )

    @patch("baresquare_sdk.aws.authentication.jwt.get_unverified_header")
    @patch("baresquare_sdk.aws.authentication.jwt.decode")
    @patch("baresquare_sdk.aws.authentication.time.time")
    def test_is_jwt_expired_false(self, mock_time, mock_jwt_decode, mock_get_header):
        """Test JWT token that is not expired."""
        # Arrange
        mock_get_header.return_value = {"alg": "RS256"}
        mock_jwt_decode.return_value = {"exp": 2000000}  # Future timestamp
        mock_time.return_value = 1000000  # Current timestamp

        # Act
        result = is_jwt_expired("test-token")

        # Assert
        assert result is False


class TestObtainAuth0Token:
    """Test suite for obtain_auth0_token function."""

    @patch("baresquare_sdk.aws.authentication.ssm.get_parameter")
    @patch("baresquare_sdk.aws.authentication.is_jwt_expired")
    @patch("baresquare_sdk.aws.authentication.logger")
    @patch.dict(os.environ, {"PL_SERVICE": "test-service", "PL_ENV": "test", "PL_REGION": "us-east-1"}, clear=True)
    def test_obtain_auth0_token_cached_valid(self, mock_logger, mock_is_expired, mock_get_ssm):
        """Test returning cached valid token."""
        # Arrange
        cached_token = "cached-token-123"
        mock_get_ssm.return_value = cached_token
        mock_is_expired.return_value = False

        # Act
        result = obtain_auth0_token(
            "test-audience-service", "test-domain.auth0.com", "test-client-id", "test-client-secret", "test-audience"
        )

        # Assert
        assert result == cached_token
        mock_get_ssm.assert_called_once_with("/test-service/test-audience-service/auth0_token")
        mock_is_expired.assert_called_once_with(cached_token)
        mock_logger.info.assert_called_once_with("Returning cached Auth0 token")

    @patch("baresquare_sdk.aws.authentication.ssm.get_parameter")
    @patch("baresquare_sdk.aws.authentication.is_jwt_expired")
    @patch("baresquare_sdk.aws.authentication.generate_auth0_token")
    @patch("baresquare_sdk.aws.authentication.ssm.put_parameter")
    @patch("baresquare_sdk.aws.authentication.logger")
    @patch.dict(os.environ, {"PL_SERVICE": "test-service", "PL_ENV": "test", "PL_REGION": "us-east-1"}, clear=True)
    def test_obtain_auth0_token_cached_expired(
        self, mock_logger, mock_put_ssm, mock_generate, mock_is_expired, mock_get_ssm
    ):
        """Test generating new token when cached token is expired."""
        # Arrange
        cached_token = "expired-token"
        new_token = "new-token-123"
        mock_get_ssm.return_value = cached_token
        mock_is_expired.return_value = True
        mock_generate.return_value = new_token

        # Act
        result = obtain_auth0_token(
            "test-audience-service", "test-domain.auth0.com", "test-client-id", "test-client-secret", "test-audience"
        )

        # Assert
        assert result == new_token
        mock_get_ssm.assert_called_once_with("/test-service/test-audience-service/auth0_token")
        mock_is_expired.assert_called_once_with(cached_token)
        mock_generate.assert_called_once_with(
            "test-domain.auth0.com", "test-client-id", "test-client-secret", "test-audience"
        )
        mock_put_ssm.assert_called_once_with(
            ssm_key="/test-service/test-audience-service/auth0_token",
            ssm_value=new_token,
            overwrite=True,
            ssm_type="SecureString",
        )
        mock_logger.info.assert_called_once_with("Auth0 token expired; generating new one")

    @patch("baresquare_sdk.aws.authentication.ssm.get_parameter")
    @patch("baresquare_sdk.aws.authentication.generate_auth0_token")
    @patch("baresquare_sdk.aws.authentication.ssm.put_parameter")
    @patch("baresquare_sdk.aws.authentication.logger")
    @patch.dict(os.environ, {"PL_SERVICE": "test-service", "PL_ENV": "test", "PL_REGION": "us-east-1"}, clear=True)
    def test_obtain_auth0_token_no_cached_token(self, mock_logger, mock_put_ssm, mock_generate, mock_get_ssm):
        """Test generating new token when no cached token exists."""
        # Arrange
        new_token = "new-token-123"
        mock_get_ssm.side_effect = Exception("Parameter not found")
        mock_generate.return_value = new_token

        # Act
        result = obtain_auth0_token(
            "test-audience-service", "test-domain.auth0.com", "test-client-id", "test-client-secret", "test-audience"
        )

        # Assert
        assert result == new_token
        mock_get_ssm.assert_called_once_with("/test-service/test-audience-service/auth0_token")
        mock_generate.assert_called_once_with(
            "test-domain.auth0.com", "test-client-id", "test-client-secret", "test-audience"
        )
        mock_put_ssm.assert_called_once_with(
            ssm_key="/test-service/test-audience-service/auth0_token",
            ssm_value=new_token,
            overwrite=True,
            ssm_type="SecureString",
        )
        mock_logger.info.assert_called_once_with(
            "Error retrieving Auth0 token from SSM: Parameter not found; generating new one"
        )


class TestCustomExceptions:
    """Test suite for custom exception classes."""

    def test_unauthorized_exception(self):
        """Test UnauthorizedException initialization."""
        exception = UnauthorizedException("Access denied")

        assert exception.status_code == 403
        assert exception.detail == "Access denied"
        assert isinstance(exception, HTTPException)

    def test_unauthenticated_exception(self):
        """Test UnauthenticatedException initialization."""
        exception = UnauthenticatedException()

        assert exception.status_code == 401
        assert exception.detail == "Requires authentication"
        assert isinstance(exception, HTTPException)


class TestAuthenticationEdgeCases:
    """Test edge cases and integration scenarios."""

    @pytest.mark.asyncio
    @patch("baresquare_sdk.aws.authentication.jwt.PyJWKClient")
    @patch.dict(
        os.environ,
        {
            "AUTH0_DOMAIN": "test-domain.auth0.com",
            "PL_ENV": "test",
            "PL_SERVICE": "test-service",
            "PL_REGION": "us-east-1",
        },
        clear=True,
    )
    async def test_verify_token_lazy_client_initialization(self, mock_pyjwk_client):
        """Test that JWKS client is initialized only when needed."""
        # Arrange
        verify_token = VerifyToken()
        assert verify_token.jwks_client is None

        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test-key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_pyjwk_client.return_value = mock_client

        mock_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")

        # Act
        with pytest.raises(UnauthorizedException):
            await verify_token.verify(security_scopes=SecurityScopes(), token=mock_token, request=None)

        # Assert
        # Client should be initialized after first call
        assert verify_token.jwks_client is not None
        mock_pyjwk_client.assert_called_once()

    @patch("baresquare_sdk.aws.authentication.jwt.get_unverified_header")
    def test_is_jwt_expired_different_algorithms(self, mock_get_header):
        """Test JWT expiration check with different algorithms."""
        # Arrange
        test_cases = [{"alg": "HS256"}, {"alg": "RS512"}, {"alg": "ES256"}]

        for case in test_cases:
            mock_get_header.return_value = case

            with (
                patch("baresquare_sdk.aws.authentication.jwt.decode") as mock_decode,
                patch("baresquare_sdk.aws.authentication.time.time", return_value=1000000),
            ):
                mock_decode.return_value = {"exp": 2000000}

                # Act
                result = is_jwt_expired("test-token")

                # Assert
                assert result is False
                mock_decode.assert_called_with(
                    jwt="test-token", algorithms=[case["alg"]], options={"verify_signature": False}
                )

    def test_generate_auth0_token_response_without_access_token(self):
        """Test generate_auth0_token when response doesn't contain access_token."""
        with patch("baresquare_sdk.aws.authentication.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"error": "invalid_client"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Act
            result = generate_auth0_token("domain", "id", "secret", "audience")

            # Assert
            assert result is None  # .get() returns None for missing key
