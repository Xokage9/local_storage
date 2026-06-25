import logging

import jwt
from jwt import PyJWKClient

from app.config import settings

logger = logging.getLogger(__name__)

jwks_client: PyJWKClient | None = None


def get_jwks_client() -> PyJWKClient:
    global jwks_client
    if jwks_client is None:
        certs_url = (
            f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
            "/protocol/openid-connect/certs"
        )
        jwks_client = PyJWKClient(certs_url)
    return jwks_client


def validate_token(token: str) -> dict | None:
    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            options={"verify_exp": True},
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid token: %s", e)
    except Exception as e:
        logger.error("Token validation error: %s", e)
    return None
