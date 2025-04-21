from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class ProductLocation(Base):
    __tablename__ = "product_location"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    replenishment_type = Column(String, nullable=True)
    reorder_point = Column(Integer, nullable=True)
    safety_stock = Column(Integer, nullable=True)
    max_stock = Column(Integer, nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)