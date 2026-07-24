from sqlalchemy import Column, String, Integer, Date
from config.database import Base


class CleanLogs(Base):
    __tablename__ = "clean_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    employee = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    logon_count = Column(Integer)
    file_count = Column(Integer)
    device_count = Column(Integer)
    email_count = Column(Integer)
    http_count = Column(Integer)