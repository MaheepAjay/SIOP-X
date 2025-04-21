from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class PurchaseOrders(Base):
    __tablename__ = "purchase_orders"

    po_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    supplier_id = Column(UUID(as_uuid=True), nullable=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    order_date = Column(Date, nullable=False)
    expected_delivery = Column(Date, nullable=True)
    quantity = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    order_type = Column(Integer, nullable=True)
