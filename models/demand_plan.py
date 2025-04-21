from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class DemandPlan(Base):
    __tablename__ = "demand_plan"

    plan_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    plan_date = Column(Date, nullable=False)
    planned_qty = Column(Integer, nullable=True)
    confidence_score = Column(Numeric, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)