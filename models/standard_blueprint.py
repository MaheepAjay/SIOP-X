# sql_models/standard_blueprint.py

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class StandardBlueprint(Base):
    __tablename__ = "standard_blueprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String, nullable=False)               # e.g., "Replenishment"
    blueprint_json = Column(JSON, nullable=False)             # full multi-method blueprint
    created_at = Column(DateTime, default=datetime.utcnow)
