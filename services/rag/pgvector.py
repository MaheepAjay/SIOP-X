# services/rag/pgvector.py
import os
from sqlalchemy.ext.asyncio import create_async_engine
from supabase.client import create_client
from langchain_community.vectorstores import SupabaseVectorStore

from core.config import settings

def get_pgvector_connection():
    """Returns a Supabase-compatible PostgREST client"""
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE  # service role key required for insert/query
    return create_client(url, key)

import asyncpg
from core.config import settings

_pgvector_pool = None

async def get_async_pgvector_pool():
    global _pgvector_pool
    if _pgvector_pool is None:
        _pgvector_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=1,
            max_size=5
        )
    return _pgvector_pool
