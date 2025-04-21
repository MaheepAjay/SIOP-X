from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class Products(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    uom = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    planning_method = Column(Numeric, nullable=True)
    last_update_time = Column(DateTime, nullable=True)
    segment = Column(String, nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False)
