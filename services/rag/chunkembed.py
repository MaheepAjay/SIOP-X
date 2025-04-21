# services/embedding_uploader.py

import uuid
from datetime import datetime, timezone
from openai import OpenAI
from core.config import settings
from supabase import create_client
from typing import List

# Constants
TABLE_NAME = "document_embeddings"
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 50

# Clients
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE)
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def chunk_and_store_embeddings(text: str, document_id: str):
    chunks = split_text_into_chunks(text)

    for i, chunk in enumerate(chunks):
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=chunk
            )
            embedding = response.data[0].embedding if response.data else None

            if not embedding:
                print(f"⚠️ No embedding returned for chunk {i}")
                continue

            insert_response = supabase.table(TABLE_NAME).insert({
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "content": chunk,
                "embedding": embedding,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()

            if insert_response.error:
                print(f"❌ Failed to insert chunk {i}: {insert_response.error}")
            else:
                print(f"✅ Chunk {i} stored successfully")

        except Exception as e:
            print(f"❌ Error embedding/storing chunk {i}: {str(e)}")
