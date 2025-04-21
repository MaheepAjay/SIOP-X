from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from openai import AsyncOpenAI
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field # Import Field
# Assuming these are in your project
from services.rag.pgvector import get_async_pgvector_pool
from core.config import settings

openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def get_embedding(text: str) -> List[float]:
    """
    Asynchronously gets the embedding for a given text using OpenAI's text-embedding-ada-002 model.

    Args:
        text (str): The text to embed.

    Returns:
        List[float]: The embedding vector.
    """
    response = await openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


def format_embedding(embedding: List[float]) -> str:
    """
    Formats an embedding vector into a string representation suitable for PostgreSQL.

    Args:
        embedding (List[float]): The embedding vector.

    Returns:
        str: The string representation of the embedding.
    """
    return "[" + ",".join(f"{x:.6f}" for x in embedding) + "]"



class SupabaseVectorRetriever(BaseRetriever):
    """
    Retriever that fetches documents from a Supabase database using vector similarity search.
    """
    company_id: str  # removed Field
    match_count: int   # removed Field

    def __init__(self, company_id: str, match_count: int = 5):
        """
        Initializes the SupabaseVectorRetriever.

        Args:
            company_id (str): The ID of the company to retrieve documents for.
            match_count (int, optional): The number of matching documents to retrieve. Defaults to 5.
        """
        super().__init__(company_id=company_id, match_count=match_count) # Pass to BaseRetriever
        self.company_id = company_id
        self.match_count = match_count
        # removed self.pydantic_config = {'arbitrary_types_allowed': True}


    async def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Asynchronously retrieves documents from Supabase that are relevant to the given query.

        Args:
            query (str): The query string.

        Returns:
            List[Document]: A list of Document objects representing the retrieved documents.
        """
        embedding = await get_embedding(query)
        embedding_str = format_embedding(embedding)

        pool = await get_async_pgvector_pool()
        async with pool.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT chunk_text, document_name, source_doc
                FROM document_embeddings
                WHERE company_id = $1
                ORDER BY embedding <#> $2::vector
                LIMIT $3
                """,
                self.company_id,
                embedding_str,
                self.match_count
            )

        return [
            Document(
                page_content=row["chunk_text"],
                metadata={
                    "document_name": row["document_name"],
                    "source": row["source_doc"]
                }
            )
            for row in rows
        ]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """
        Asynchronously retrieves documents from Supabase that are relevant to the given query.
        This is an alias for get_relevant_documents to satisfy the BaseRetriever interface.

        Args:
            query (str): The query string.

        Returns:
            List[Document]: A list of Document objects representing the retrieved documents.
        """
        return await self.get_relevant_documents(query)



# Wrapper to create full RetrievalQA chain
async def get_document_answer_chain(company_id: str, stream: bool = False) -> RetrievalQA:
    """
    Creates a RetrievalQA chain for answering questions based on documents from Supabase.

    Args:
        company_id (str): The ID of the company to retrieve documents for.
        stream (bool, optional): Whether to enable streaming of the LLM response. Defaults to False.

    Returns:
        RetrievalQA: The RetrievalQA chain.
    """
    retriever = SupabaseVectorRetriever(company_id=company_id)
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        streaming=stream,
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
    )



async def query_vector_store(query: str, company_id: str) -> dict:
    """
    Queries the vector store for documents relevant to the given query and company ID.

    Args:
        query (str): The query string.
        company_id (str): The ID of the company.

    Returns:
        dict: The result of the query.
    """
    return await get_document_answer_chain(company_id=company_id).arun(query)
