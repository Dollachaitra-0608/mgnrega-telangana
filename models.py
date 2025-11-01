# models.py
from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

class MGNREGAData(Base):
    __tablename__ = "mgnrega_data"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String, index=True)
    month = Column(String, index=True, default="")
    year = Column(Integer, index=True, default=0)
    households_worked = Column(Integer, default=0)
    persondays_generated = Column(Float, default=0.0)
    total_wages = Column(Float, default=0.0)
    raw_json = Column(JSON, nullable=True)
