from sqlalchemy import Column, String, Integer, Date
from config.database import Base

class RawLogs(Base):
    __tablename__ = "raw_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅ ADD THIS

    employee = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    logon_count = Column(Integer)
    file_count = Column(Integer)
    device_count = Column(Integer)
    email_count = Column(Integer)
    http_count = Column(Integer)