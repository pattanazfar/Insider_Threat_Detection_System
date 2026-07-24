from sqlalchemy import Column, String, Integer
from config.database import Base

class BlockedEmployee(Base):
    __tablename__ = "blocked_employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee = Column(String, nullable=False, unique=True)