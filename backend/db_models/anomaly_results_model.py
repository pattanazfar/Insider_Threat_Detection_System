from sqlalchemy import Column, String, Float, Integer, Date
from config.database import Base

class AnomalyResults(Base):
    __tablename__ = "anomaly_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    employee = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    anomaly_score = Column(Float)
    risk_score = Column(Float)
    is_anomaly = Column(Integer)
    risk_level = Column(String(10))