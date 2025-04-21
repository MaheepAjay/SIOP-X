from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    snapshot_date = Column(Date, nullable=False)
    on_hand_qty = Column(Integer, nullable=True)
    safety_stock = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)



from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid


class OnHandInventory(Base):
    __tablename__ = "on_hand_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    quantity = Column(Numeric(12, 2), nullable=False, default=0)
    uom = Column(String, default="EA")
    updated_at = Column(DateTime, default=datetime.utcnow)
