import uuid
from datetime import datetime
from typing import List

from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.document_embeddings import DocumentEmbedding
from services.rag.chunker import chunk_text
from services.rag.process_all_docs import BUCKET_NAME, get_existing_file_ids
from services.rag.supabase_loader import list_documents, download_document

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    if not chunks:
        return []
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=chunks
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        raise RuntimeError(f"Embedding failed: {str(e)}")


async def embed_all_documents_from_supabase(db: AsyncSession):
    print("🚀 Starting embedding process...")

    existing_docs = await get_existing_file_ids(db)
    all_files = list_documents()  # returns List[str]

    for file_name in all_files:  # file_name is already a string
        if not file_name or file_name in existing_docs:
            continue

        print(f"📄 Processing {file_name}")

        try:
            content = download_document(file_name)
            if not content:
                print(f"⚠️ Empty or unreadable file: {file_name}")
                continue

            chunks = chunk_text(content)
            print(f"✂️ {len(chunks)} chunks created for {file_name}")

            embeddings = embed_chunks(chunks)
            print(f"🧠 Embeddings generated")

            for chunk_text_val, embedding_vector in zip(chunks, embeddings):
                embedding_record = DocumentEmbedding(
                    id=str(uuid.uuid4()),
                    document_id=None,
                    source_doc=file_name,
                    chunk_text=chunk_text_val,
                    content=chunk_text_val,
                    embedding=embedding_vector,
                    created_at=datetime.utcnow(),
                    document_name = file_name,
                    company_id = "c596d0b0-598f-48bd-9a4a-85db7b1d7eb5"  # or any other company ID
                )
                db.add(embedding_record)

            await db.commit()
            print(f"✅ {file_name} embedded and stored.\n")

        except Exception as e:
            print(f"❌ Failed to process {file_name}: {str(e)}")
