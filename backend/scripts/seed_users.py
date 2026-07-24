import os

from api.schemas import USERNAME_PATTERN
from config.database import SessionLocal
from db_models.user_model import User
from security.password import hash_password

MIN_ADMIN_PASSWORD_LENGTH = 12


def load_admin_credentials() -> tuple[str, str]:
    username = os.getenv("SEED_ADMIN_USERNAME", "admin").strip()
    password = os.getenv("SEED_ADMIN_PASSWORD", "")

    if not USERNAME_PATTERN.fullmatch(username):
        raise RuntimeError(
            "SEED_ADMIN_USERNAME must be 3-50 characters and contain only "
            "letters, numbers, underscores, dots, or hyphens"
        )
    if len(password) < MIN_ADMIN_PASSWORD_LENGTH:
        raise RuntimeError(
            f"SEED_ADMIN_PASSWORD must be at least {MIN_ADMIN_PASSWORD_LENGTH} characters"
        )

    return username, password


def seed_users() -> None:
    username, password = load_admin_credentials()
    session = SessionLocal()

    try:
        admin = session.query(User).filter(User.username == username).one_or_none()
        password_hash = hash_password(password)

        if admin:
            admin.password_hash = password_hash
            admin.role = "ADMIN"
            admin.is_active = True
        else:
            session.add(
                User(
                    username=username,
                    password_hash=password_hash,
                    role="ADMIN",
                    is_active=True,
                )
            )

        session.commit()
        print("Admin user created or updated")

    except Exception:
        session.rollback()
        print("Admin seed failed")
        raise

    finally:
        session.close()


if __name__ == "__main__":
    seed_users()
