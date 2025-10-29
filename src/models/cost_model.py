from sqlalchemy import Column, Integer, String, Float, Date
from src.models.database import Base

class CloudCost(Base):
    __tablename__ = "cloud_costs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    service = Column(String(100), index=True)
    cost = Column(Float)
    usage = Column(Float)
    account_id = Column(String(50), index=True)
