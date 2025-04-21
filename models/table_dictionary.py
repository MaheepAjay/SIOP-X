from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base

class TableDictionary(Base):
    __tablename__ = "table_dictionary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String, nullable=False)
    column_name = Column(String, nullable=False)
    business_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    example = Column(String, nullable=True)
    data_type = Column(String, nullable=True)