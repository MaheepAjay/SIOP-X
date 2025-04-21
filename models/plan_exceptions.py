from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class PlanExceptions(Base):
    __tablename__ = "plan_exceptions"

    exception_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    exception_date = Column(Date, nullable=True)
    exception_type = Column(String, nullable=True)
    description = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    resolved = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=True)