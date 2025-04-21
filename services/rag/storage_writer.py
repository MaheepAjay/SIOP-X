from sqlalchemy.ext.asyncio import AsyncSession
from models.document_embeddings import DocumentEmbedding
from uuid import uuid4
from datetime import datetime

async def store_embeddings(chunks, document_name, company_id, db: AsyncSession):
    for chunk in chunks:
        content_text = chunk.get("text", "")  # fallback to empty string if not found
        print("🧩 Chunk content preview:", content_text[:100])  # debug print
        db.add(DocumentEmbedding(
            id=str(uuid4()),
            company_id=company_id,
            document_name=document_name,
            content=chunk['text'],
            embedding=chunk['embedding'],
            created_at=datetime.utcnow()
        ))
    await db.commit()
