# models/calendar.py

from sqlalchemy import Column, Date, Integer, String
from core.database import Base

class Calendar(Base):
    __tablename__ = "calendar"

    calendar_date = Column(Date, primary_key=True)  # 👈 Fix here
    week_number = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    fiscal_period = Column(String, nullable=True)
