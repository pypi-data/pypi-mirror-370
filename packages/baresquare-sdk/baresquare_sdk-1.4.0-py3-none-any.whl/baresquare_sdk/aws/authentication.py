"""Authentication and authorization utilities for Auth0/JWT integration.

Provides:
- JWT validation middleware for FastAPI
- Auth0 token generation and management
- AWS SSM integration for secure token storage
- Custom exception classes for authentication errors
- Token expiration handling and automatic renewal

Dependencies: PyJWT, FastAPI, requests
"""

import logging
import time

import jwt
import requests
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from baresquare_sdk.aws import ssm
from baresquare_sdk.settings import get_settings

logger = logging.getLogger(__name__)


DEFAULT_CREDS = Depends(HTTPBearer())


class UnauthorizedException(HTTPException):
    """Exception raised when a request fails authorization checks.

    Attributes
        detail: Human-readable explanation of the authorization failure

    """

    def __init__(self, detail: str, **kwargs):
        """Initialize with 403 status code and error details."""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    """Exception raised when no authentication credentials are provided."""

    def __init__(self):
        """Initialize with 401 status code and generic message."""
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication")


class VerifyToken:
    """JWT validation handler for FastAPI endpoints.

    Uses Auth0's JWKS endpoint to verify token signatures and validate claims.

    Attributes
        jwks_client: PyJWKClient instance for fetching JSON Web Key Sets

    """

    def __init__(self):
        """Initialize with empty JWKS client (lazy-loaded when needed)."""
        self.jwks_client = None

    def initialize_client(self):
        """Initialize the JWKS client with Auth0 domain configuration."""
        settings = get_settings()
        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: HTTPAuthorizationCredentials | None = DEFAULT_CREDS,
        request: Request = None,
    ) -> dict:
        """Validate JWT token and return decoded payload.

        Args:
            security_scopes: FastAPI security scope requirements
            token: Bearer token from Authorization header
            request: FastAPI request object from the call to the API endpoint

        Returns:
            Decoded JWT payload if validation succeeds

        Raises:
            UnauthenticatedException: No token provided
            UnauthorizedException: Token validation failed

        """
        if token is None:
            raise UnauthenticatedException

        if self.jwks_client is None:
            self.initialize_client()

        # This gets the 'kid' from the passed token
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token.credentials).key
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error)) from error
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error)) from error

        try:
            settings = get_settings()
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms="RS256",
                audience=settings.auth0_api_audience,
                issuer=f"https://{settings.auth0_domain}/",
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        # Store payload in request.state for the logging dependency
        if request is not None:
            request.state.auth_payload = payload

        return payload


def generate_auth0_token(
    auth0_domain: str,
    auth0_client_id: str,
    auth0_client_secret: str,
    auth0_audience: str,
) -> str:
    """Obtain new Auth0 access token using client credentials flow.

    Args:
        auth0_domain: Auth0 tenant domain
        auth0_client_id: Application client ID
        auth0_client_secret: Application client secret
        auth0_audience: API audience identifier

    Returns:
        Access token string

    Raises:
        HTTPError: If token request fails

    """
    url = f"https://{auth0_domain}/oauth/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = {
        "client_id": auth0_client_id,
        "client_secret": auth0_client_secret,
        "audience": auth0_audience,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json().get("access_token")


def is_jwt_expired(access_token: str) -> bool:
    """Check if a JWT token has expired without validating signature.

    Args:
        access_token: JWT token string

    Returns:
        True if token expiration time has passed, False otherwise

    """
    jwt_algo = jwt.get_unverified_header(jwt=access_token).get("alg")
    payload = jwt.decode(jwt=access_token, algorithms=[jwt_algo], options={"verify_signature": False})
    expiration_timestamp = payload.get("exp")
    current_timestamp = int(time.time())
    return expiration_timestamp < current_timestamp


def obtain_auth0_token(
    audience_service: str,
    auth0_domain: str,
    auth0_client_id: str,
    auth0_client_secret: str,
    auth0_audience: str,
) -> str:
    """Get valid Auth0 token from cache or generate new one.

    Args:
        audience_service: Service name for SSM parameter key
        auth0_domain: Auth0 tenant domain
        auth0_client_id: Application client ID
        auth0_client_secret: Application client secret
        auth0_audience: API audience identifier

    Returns:
        Valid access token string

    Side effects:
        Updates SSM parameter store with new token when expired, missing, or invalid

    """
    settings = get_settings()
    ssm_key = f"/{settings.pl_service}/{audience_service}/auth0_token"

    try:
        # Get and returned the cached token
        cached_token = ssm.get_parameter(ssm_key)
        if is_jwt_expired(cached_token):
            logger.info("Auth0 token expired; generating new one")
        else:
            logger.info("Returning cached Auth0 token")
            return cached_token
    except Exception as e:
        # Handle case where SSM key doesn't exist or other errors
        logger.info(f"Error retrieving Auth0 token from SSM: {str(e)}; generating new one")

    # Generate, store and return new token
    token = generate_auth0_token(auth0_domain, auth0_client_id, auth0_client_secret, auth0_audience)
    ssm.put_parameter(ssm_key=ssm_key, ssm_value=token, overwrite=True, ssm_type="SecureString")
    return token
