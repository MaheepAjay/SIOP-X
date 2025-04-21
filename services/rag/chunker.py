from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str) -> List[str]:
    chunks = []
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        if para.strip():
            enriched_chunk = f"Document Context: {para.strip()}"
            chunks.append(enriched_chunk)
    return chunks
