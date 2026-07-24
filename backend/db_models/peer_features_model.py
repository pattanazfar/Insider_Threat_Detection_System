from sqlalchemy import Column, String, Integer, Float, Date
from config.database import Base


class PeerFeatures(Base):
    __tablename__ = "peer_features"

    id = Column(Integer, primary_key=True, autoincrement=True)

    employee = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    logon_count_peer_diff = Column(Float)
    logon_count_peer_zscore = Column(Float)

    file_count_peer_diff = Column(Float)
    file_count_peer_zscore = Column(Float)

    device_count_peer_diff = Column(Float)
    device_count_peer_zscore = Column(Float)

    email_count_peer_diff = Column(Float)
    email_count_peer_zscore = Column(Float)

    http_count_peer_diff = Column(Float)
    http_count_peer_zscore = Column(Float)

    peer_deviation_score = Column(Float)