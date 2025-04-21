from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class DemandPlans(Base):
    __tablename__ = "demand_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    forecast_date = Column(Date, nullable=False)
    forecast_quantity = Column(Numeric, nullable=True)
    hard_demand_quantity = Column(Numeric, nullable=True)
    total_demand = Column(Numeric, nullable=True)
    method = Column(String, nullable=True)
    version = Column(String, nullable=True)
    policy_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=True)
    company_id = Column(UUID(as_uuid=True), nullable=True)