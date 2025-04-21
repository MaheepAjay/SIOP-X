from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class ForecastingPolicies(Base):
    __tablename__ = "forecasting_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=True)
    domain = Column(String, nullable=False)
    rule_type = Column(String, nullable=False)
    frequency = Column(String, nullable=True)
    method = Column(String, nullable=True)
    conditions = Column(String, nullable=True)
    logic = Column(String, nullable=True)
    extracted_at = Column(DateTime(timezone=True), nullable=True)
    segment = Column(String, nullable=True)
    document_id = Column(UUID(as_uuid=True), nullable=True)