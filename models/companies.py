from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class Companies(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True)