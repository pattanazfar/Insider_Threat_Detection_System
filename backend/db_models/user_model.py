from sqlalchemy import Column, Integer, String, Boolean
from config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)