from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings

engine_options = {"echo": False}
if not settings.database_url.startswith("sqlite"):
    engine_options.update({"pool_size": 5, "max_overflow": 5, "pool_timeout": 30, "pool_recycle": 1800, "pool_pre_ping": True})

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
