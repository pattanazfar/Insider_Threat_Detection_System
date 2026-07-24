from sqlalchemy import Column, String, Integer, Float, Date
from config.database import Base


class FinalFeatures(Base):
    __tablename__ = "final_features"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ===============================
    # IDENTIFIERS
    # ===============================
    employee = Column(String(100))
    date = Column(Date)

    # ===============================
    # RAW COUNTS
    # ===============================
    logon_count = Column(Integer)
    file_count = Column(Integer)
    device_count = Column(Integer)
    email_count = Column(Integer)
    http_count = Column(Integer)

    # ===============================
    # TOTAL ACTIVITY
    # ===============================
    total_activity = Column(Float)

    # ===============================
    # RATIOS
    # ===============================
    logon_ratio = Column(Float)
    file_ratio = Column(Float)
    device_ratio = Column(Float)
    email_ratio = Column(Float)
    http_ratio = Column(Float)

    # ===============================
    # LOG FEATURES
    # ===============================
    logon_log = Column(Float)
    file_log = Column(Float)
    device_log = Column(Float)
    email_log = Column(Float)
    http_log = Column(Float)

    # ===============================
    # FLAGS
    # ===============================
    high_file_activity = Column(Integer)
    high_http_activity = Column(Integer)

    # ===============================
    # SCORES
    # ===============================
    behavior_deviation_score = Column(Float)
    resource_access_score = Column(Float)