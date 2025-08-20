"""Authentication utilities for bot builder service."""

from typing import Any, Dict, Optional

import jwt
from jwt import PyJWKClient
from pydantic import BaseModel

from rasa.builder.config import AUTH0_CLIENT_ID, AUTH0_ISSUER, JWKS_URL

HEADER_USER_ID = "X-User-Id"


def verify_auth0_token(token: str) -> Dict[str, Any]:
    """Verify JWT token from Auth0.

    Args:
        token: JWT token string

    Returns:
        Dict containing the token payload

    Raises:
        Exception: If token verification fails
    """
    jwk_client = PyJWKClient(JWKS_URL)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=AUTH0_CLIENT_ID,
        issuer=AUTH0_ISSUER,
    )
    return payload


class Auth0TokenVerificationResult(BaseModel):
    payload: Optional[Dict[str, Any]]
    error_message: Optional[str]


def extract_and_verify_auth0_token(
    auth_header: str,
) -> Auth0TokenVerificationResult:
    """Extract and verify JWT token from Authorization header.

    Args:
        auth_header: Authorization header value

    Returns:
        Auth0TokenVerificationResult: Contains payload and error_message.
    """
    # Check Authorization header format
    if not auth_header.startswith("Bearer "):
        return Auth0TokenVerificationResult(
            payload=None, error_message="Missing or invalid Authorization header"
        )

    # Extract token
    token = auth_header.split(" ")[1]

    # Verify token
    try:
        payload = verify_auth0_token(token)
        return Auth0TokenVerificationResult(payload=payload, error_message=None)
    except Exception as e:
        return Auth0TokenVerificationResult(
            payload=None, error_message=f"Invalid token: {e!s}"
        )
