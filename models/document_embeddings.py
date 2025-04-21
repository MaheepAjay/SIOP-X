from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

from core.database import Base  # or declarative_base() if outside FastAPI project

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    document_name = Column(String, nullable=False)  # filename from Supabase Storage
    content = Column(Text, nullable=False)          # chunked text
    embedding = Column(Vector(1536), nullable=False)  # assuming OpenAI embedding size
    created_at = Column(DateTime, default=datetime.utcnow)
    source_doc = Column(String, nullable=True)  # 🔧 Add this
    document_id = Column(UUID(as_uuid=True), nullable=True)  # ✅ Add this line
    chunk_text = Column(String, nullable=False)  # ✅ Add this
    document_name = Column(String, nullable=True)  # if you're keeping it




class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    document_name = Column(String, nullable=False)
    document_type = Column(String, nullable=True)  # e.g., 'policy', 'SOP', 'manual'
    uploaded_by = Column(String, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    tags = Column(ARRAY(String), nullable=True)
    version = Column(String, nullable=True)
    language = Column(String, nullable=True)
    status = Column(String, default="processed")  # processed, failed, pending
    notes = Column(String, nullable=True)
