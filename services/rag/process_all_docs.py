import asyncio
import uuid
from datetime import datetime
from typing import List

from openai import OpenAI
from core.config import settings
from services.rag.supabase_loader import list_documents, download_document
from services.rag.chunker import chunk_text
from services.rag.storage_writer import store_embeddings
from core.database import get_async_session
from models.document_embeddings import DocumentEmbedding
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)
BUCKET_NAME = "documents"

def get_embedding(text: str):
    if not text:
        return None
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

async def get_existing_file_ids(db: AsyncSession) -> List[str]:
    result = await db.execute(select(DocumentEmbedding.source_doc).distinct())
    return [row[0] for row in result.fetchall()]

async def process_all(company_id: str = "demo"):
    async with get_async_session() as db:
        existing_files = await get_existing_file_ids(db)
        files = list_documents()

        for file_name in files:
            if file_name in existing_files:
                print(f"⚠️ Skipping {file_name}, already embedded.")
                continue

            print(f"📄 Processing {file_name}")
            text = download_document(file_name)
            chunks = chunk_text(text)
            embedded_chunks = [{"text": c, "embedding": get_embedding(c)} for c in chunks]
            await store_embeddings(embedded_chunks, file_name, company_id, db)

if __name__ == "__main__":
    asyncio.run(process_all())
