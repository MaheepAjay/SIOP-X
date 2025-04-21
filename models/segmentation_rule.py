# sql_models/segmentation_rule.py

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class SegmentationRule(Base):
    __tablename__ = "segmentation_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID, nullable=False)
    segment_name = Column(String, nullable=False)
    rule_description = Column(Text, nullable=True)
    rule_expression = Column(Text, nullable=False)  # logic string like SQL WHERE clause
    created_at = Column(DateTime, default=datetime.utcnow)
