# Data Models for Rule-driven Autonomous Agent System

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


class OutputConfig(Base):
    __tablename__ = "output_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_type = Column(String, nullable=False)  # CSV, Excel, etc.
    columns = Column(JSON, nullable=False)  # e.g. ["product_id", "forecast_qty"]
    destination = Column(String, nullable=True)  # storage path, email, webhook, etc.

class UserAction(Base):
    __tablename__ = "user_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    action_type = Column(String, nullable=False)  # generate_file, run_forecast
    description = Column(String, nullable=True)
    target_segment = Column(String, nullable=True)
    trigger_type = Column(String, nullable=True)  # manual, scheduled, etc.
    frequency = Column(String, nullable=True)
    output_config_id = Column(UUID(as_uuid=True), ForeignKey("output_configs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    document_id = Column(UUID(as_uuid=True), nullable=True)  # 👈 ADD THIS
    status = Column(String, nullable=False, default="pending")



    output_config = relationship("OutputConfig")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)  # forecast_generator, file_writer
    rule_id = Column(UUID(as_uuid=True), ForeignKey("document_rules.id"), nullable=True)
    action_id = Column(UUID(as_uuid=True), ForeignKey("user_actions.id"), nullable=True)
    status = Column(String, default="active")
    last_run = Column(DateTime, nullable=True)
    config = Column(JSON, nullable=True)

    rule = relationship("DocumentRules")
    action = relationship("UserAction")

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    step_order = Column(JSON, nullable=False)  # list of agent_ids
    trigger_type = Column(String, default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)

    