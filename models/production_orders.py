from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class ProductionOrders(Base):
    __tablename__ = "production_orders"

    prod_order_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    quantity = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)