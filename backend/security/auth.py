from config.database import SessionLocal
from db_models.user_model import User

from security.password import verify_password
from security.jwt import create_token


def authenticate(username: str, password: str):
    session = SessionLocal()

    try:
        user = session.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        token = create_token(user.username, user.role)

        return {
            "username": user.username,
            "role": user.role,
            "token": token
        }

    finally:
        session.close()
