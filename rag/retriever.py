# ==============================================================================
# JEE MENTOR AI - RAG RETRIEVAL ENGINE
# ==============================================================================
from typing import List, Dict, Any, Optional
from rag.vector_store import JEEVectorStore

class JEERetriever:
    def __init__(self, db_path: str = "./data/chroma"):
        """Establishes connection to the underlying vector store."""
        self.db = JEEVectorStore(persist_directory=db_path)

    def retrieve_context(self, query: str, k: int = 3, subject: Optional[str] = None, topic: Optional[str] = None) -> str:
        """Searches ChromaDB for relevant formulas/theory and formats them into a clean prompt context."""
        
        # Build search filters dynamically if provided
        filter_dict = {}
        if subject:
            filter_dict["subject"] = subject
        if topic:
            filter_dict["topic"] = topic
            
        filters = filter_dict if filter_dict else None
        
        # Perform semantic lookup
        # Cosine distance returns values where lower distance is better, 
        # so similarity = 1 - distance. We prune below 0.35 similarity (noise threshold)
        raw_results = self.db.similarity_search(query, k=k, filter_dict=filters)
        
        if not raw_results:
            return "No matching reference material or formulas found in the database."

        formatted_blocks = []
        for index, (text, meta, score) in enumerate(raw_results):
            if score < 0.35: # Ignore highly divergent vectors to prevent prompt diluting
                continue
                
            block_header = f"Reference #{index+1} [{meta.get('subject')} - {meta.get('topic')} ({meta.get('type')}) | Relevance: {score*100:.1f}%]"
            formatted_block = f"--- {block_header} ---\n{text}"
            formatted_blocks.append(formatted_block)

        if not formatted_blocks:
            return "No highly relevant formulas or NCERT notes found for this concept."

        return "\n\n".join(formatted_blocks)

    def retrieve_formulas_only(self, query: str, k: int = 2) -> List[str]:
        """Specific helper to extract formula strings only, useful for calculator and SymPy tools."""
        raw_results = self.db.similarity_search(query, k=k)
        
        formulas = []
        for text, meta, score in raw_results:
            if meta.get("type") == "Formula" and score > 0.4:
                formulas.append(text)
        return formulas

if __name__ == "__main__":
    retriever = JEERetriever()
    context = retriever.retrieve_context("Ohm's law resistance voltage")
    print("\n[SUCCESS] Retrieved Context Preview:")
    print(context)
