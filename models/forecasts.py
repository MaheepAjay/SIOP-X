from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class Forecasts(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    sku = Column(String, nullable=True)
    forecast_date = Column(Date, nullable=True)
    forecast_qty = Column(String, nullable=True)
    method = Column(String, nullable=True)
    policy_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=True)
    location_id = Column(UUID(as_uuid=True), nullable=False)


from sqlalchemy import Column, String, Date, Numeric, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Forecast(Base):
    __tablename__ = "forecast"

    id = Column(UUID(as_uuid=True), primary_key=True)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    location_id = Column(UUID(as_uuid=True), nullable=False)
    forecast_date = Column(Date, nullable=False)
    forecast_quantity = Column(Numeric, nullable=False)
    method = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
