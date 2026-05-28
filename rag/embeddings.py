# ==============================================================================
# JEE MENTOR AI - RAG EMBEDDINGS SERVICE
# ==============================================================================
import os
from typing import List, Union
import numpy as np

class JEEEmbeddings:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initializes the sentence-transformers local model, handling CPU/GPU logic."""
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads the sentence-transformer model in a lazy fashion, utilizing GPU if available."""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[INFO] Initializing Embedding Model '{self.model_name}' on device '{device}'...")
            self.model = SentenceTransformer(self.model_name, device=device)
            print("[SUCCESS] Embedding Model loaded successfully.")
        except ImportError:
            print("[WARNING] sentence-transformers or torch is not installed. RAG will fall back to a mock embedding generator for testing.")
            self.model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of document strings."""
        if self.model is not None:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]
        else:
            # High-yield deterministic mock embeddings for headless/dependency-free testing
            return [self._mock_embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Generates embedding for a single search query."""
        if self.model is not None:
            embedding = self.model.encode(text, show_progress_bar=False)
            return embedding.tolist()
        else:
            return self._mock_embed(text)

    def _mock_embed(self, text: str, dimension: int = 384) -> List[float]:
        """Programmatic helper to return mock embeddings of dimension 384 based on word hash seeds."""
        import hashlib
        h = hashlib.md5(text.encode('utf-8')).hexdigest()
        seed = int(h, 16) % 10000
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(dimension)
        # L2 Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

if __name__ == "__main__":
    emb_service = JEEEmbeddings()
    sample = "Calculate the electric potential of a sphere."
    vec = emb_service.embed_query(sample)
    print(f"[SUCCESS] Generated embedding vector of length: {len(vec)}")
