import datetime
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base


class DocumentRules(Base):
    __tablename__ = "document_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    document_id = Column(UUID(as_uuid=True), nullable=True)
    domain = Column(String, nullable=False)
    rule_type = Column(String, nullable=True)
    frequency = Column(String, nullable=True)
    method = Column(String, nullable=True)
    segment = Column(String, nullable=True)
    conditions = Column(String, nullable=True)
    logic = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    source_doc = Column(String, nullable=True)
    extracted_by = Column(String, nullable=True)
    extracted_at = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_id = Column(UUID(as_uuid=True), ForeignKey("agent_metadata.id"), nullable=True)  # 🧠 New

     