# sql_models/agent_metadata.py

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class AgentMetadata(Base):
    __tablename__ = "agent_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    segment = Column(String, nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    policy_id = Column(UUID(as_uuid=True), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    additional_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
