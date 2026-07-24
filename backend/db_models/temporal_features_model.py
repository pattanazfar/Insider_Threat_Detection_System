from sqlalchemy import Column, String, Integer, Float, Date
from config.database import Base


class TemporalFeatures(Base):
    __tablename__ = "temporal_features"

    id = Column(Integer, primary_key=True, autoincrement=True)

    employee = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    logon_count_mean_7d = Column(Float)
    logon_count_mean_30d = Column(Float)
    logon_count_delta = Column(Float)
    logon_count_zscore = Column(Float)

    file_count_mean_7d = Column(Float)
    file_count_mean_30d = Column(Float)
    file_count_delta = Column(Float)
    file_count_zscore = Column(Float)

    device_count_mean_7d = Column(Float)
    device_count_mean_30d = Column(Float)
    device_count_delta = Column(Float)
    device_count_zscore = Column(Float)

    email_count_mean_7d = Column(Float)
    email_count_mean_30d = Column(Float)
    email_count_delta = Column(Float)
    email_count_zscore = Column(Float)

    http_count_mean_7d = Column(Float)
    http_count_mean_30d = Column(Float)
    http_count_delta = Column(Float)
    http_count_zscore = Column(Float)

    temporal_deviation_score = Column(Float)