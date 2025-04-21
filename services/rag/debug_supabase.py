from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.embeddings import Embeddings
from typing import List, Tuple, Optional
import numpy as np

class DebugSupabaseVectorStore(SupabaseVectorStore):

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        **kwargs
    ) -> List[Tuple[str, float]]:
        docs_and_scores = super().similarity_search_with_score(query, k=k, **kwargs)

        print(f"\n🔍 Similarity scores for query: \"{query}\"")
        for doc, score in docs_and_scores:
            name = doc.metadata.get("document_name", "Unknown")
            snippet = doc.page_content[:120].replace("\n", " ")
            print(f"• {name}: score={score:.4f} | content: {snippet}...\n")

        return docs_and_scores
