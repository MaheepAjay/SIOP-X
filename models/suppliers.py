from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class Suppliers(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(UUID(as_uuid=True), nullable=False,primary_key=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)