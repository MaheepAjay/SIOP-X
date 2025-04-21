from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class Documents(Base):
    __tablename__ = "documents"

    filename = Column(String, nullable=False)
    content = Column(String, nullable=False)
    extracted = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)