# ==============================================================================
# JEE MENTOR AI - CHROMADB VECTOR STORE MANAGER
# ==============================================================================
import os
from typing import List, Dict, Any, Tuple, Optional
from rag.embeddings import JEEEmbeddings

class JEEVectorStore:
    def __init__(self, persist_directory: str = "./data/chroma", collection_name: str = "jee_knowledge"):
        """Initializes ChromaDB local client and links it to our collection."""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_service = JEEEmbeddings()
        self.client = None
        self.collection = None
        self._initialize_chroma()

    def _initialize_chroma(self):
        """Prepares the persistent storage directory and establishes the collection connection."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            print(f"[INFO] Initializing ChromaDB at: {self.persist_directory}")
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"} # Use cosine similarity for normalization
            )
            print(f"[SUCCESS] ChromaDB collection '{self.collection_name}' is active.")
        except ImportError:
            print("[WARNING] ChromaDB package is not installed. Entering Mock Vector Store mode.")
            self.client = None
            self.collection = None
            self.mock_db = [] # Fallback list of dicts for local CPU headless mock dev

    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Generates embeddings and inserts documents into ChromaDB."""
        if not texts:
            return
            
        embeddings = self.embedding_service.embed_documents(texts)
        
        if self.collection is not None:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[SUCCESS] Added {len(texts)} documents to ChromaDB.")
        else:
            # Mock mode implementation
            for i, text in enumerate(texts):
                self.mock_db.append({
                    "id": ids[i],
                    "text": text,
                    "metadata": metadatas[i],
                    "embedding": embeddings[i]
                })
            print(f"[MOCK] Added {len(texts)} documents to local Mock DB memory.")

    def similarity_search(self, query: str, k: int = 4, filter_dict: Optional[Dict[str, Any]] = None) -> List[Tuple[str, Dict[str, Any], float]]:
        """Queries the vector database using cosine distance and returns (document, metadata, score) tuples."""
        query_vector = self.embedding_service.embed_query(query)
        
        if self.collection is not None:
            # Query chroma
            where_clause = filter_dict if filter_dict else None
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            if results and results["documents"] and len(results["documents"][0]) > 0:
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                dists = results["distances"][0]
                
                for idx in range(len(docs)):
                    # Cosine distance to cosine similarity: similarity = 1 - distance
                    sim_score = 1.0 - dists[idx]
                    formatted_results.append((docs[idx], metas[idx], sim_score))
                    
            return formatted_results
        else:
            # Mock Mode search (linear cosine similarity lookup)
            import numpy as np
            q_arr = np.array(query_vector)
            
            mock_results = []
            for item in self.mock_db:
                # Optional filtering
                if filter_dict:
                    matches = True
                    for fkey, fval in filter_dict.items():
                        if item["metadata"].get(fkey) != fval:
                            matches = False
                            break
                    if not matches:
                        continue
                        
                i_arr = np.array(item["embedding"])
                sim = np.dot(q_arr, i_arr) / (np.linalg.norm(q_arr) * np.linalg.norm(i_arr) + 1e-9)
                mock_results.append((item["text"], item["metadata"], float(sim)))
                
            # Sort by similarity descending
            mock_results.sort(key=lambda x: x[2], reverse=True)
            return mock_results[:k]

if __name__ == "__main__":
    db = JEEVectorStore(persist_directory="./data/chroma_test")
    db.add_documents(
        texts=["Coulomb's law formula is F = k * q1 * q2 / r^2", "Ohm's law formula is V = I * R"],
        metadatas=[{"subject": "Physics", "topic": "Electrostatics"}, {"subject": "Physics", "topic": "Current"}],
        ids=["id1", "id2"]
    )
    res = db.similarity_search("What is the formula for electric charge force?", k=1)
    print(f"[SUCCESS] Search Query Results: {res}")
