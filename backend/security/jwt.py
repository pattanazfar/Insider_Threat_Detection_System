from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from config.settings import settings

ALGORITHM = "HS256"
ISSUER = "insider-threat-api"
AUDIENCE = "insider-threat-frontend"


def create_token(username: str, role: str) -> str:
    now = datetime.now(UTC)
    payload = {"sub": username, "role": role, "iss": ISSUER, "aud": AUDIENCE, "iat": now, "nbf": now, "exp": now + timedelta(minutes=settings.token_exp_minutes), "jti": str(uuid4())}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM], issuer=ISSUER, audience=AUDIENCE, options={"require": ["sub", "role", "exp", "iat", "nbf", "jti"]})
