from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class SalesOrders(Base):
    __tablename__ = "sales_orders"

    order_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    customer_id = Column(UUID(as_uuid=True), nullable=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    order_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    uom = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)
