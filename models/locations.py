from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class Locations(Base):
    __tablename__ = "locations"

    location_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    region = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)