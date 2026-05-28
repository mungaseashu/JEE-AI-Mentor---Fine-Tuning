# ==============================================================================
# JEE MENTOR AI - RAG SYSTEM INTEGRATION TESTS
# ==============================================================================
import os
import pytest
from rag.embeddings import JEEEmbeddings
from rag.vector_store import JEEVectorStore
from rag.retriever import JEERetriever

@pytest.fixture(scope="module")
def temp_db_path():
    path = "./data/chroma_test_run"
    yield path
    # Cleanup after test completion
    import shutil
    if os.path.exists(path):
        shutil.rmtree(path)

def test_embeddings_generation():
    """Asserts embedding service generates correct normalized vectors."""
    emb = JEEEmbeddings()
    text = "Calculate Planck's constant"
    vec = emb.embed_query(text)
    
    assert isinstance(vec, list)
    # MiniLM-L6-v2 vector dimension must be 384
    assert len(vec) == 384
    
    # Assert L2 Normalization (norm ≈ 1.0)
    import numpy as np
    norm = np.linalg.norm(vec)
    assert pytest.approx(norm, abs=1e-3) == 1.0

def test_vector_store_operations(temp_db_path):
    """Asserts documents insert correctly and queries return valid scores."""
    db = JEEVectorStore(persist_directory=temp_db_path, collection_name="test_collection")
    
    docs = [
        "First-order reactions half-life is t_1/2 = 0.693 / k.",
        "Ohm's law resistance matches V = I * R."
    ]
    metas = [
        {"subject": "Chemistry", "topic": "Kinetics", "type": "Formula"},
        {"subject": "Physics", "topic": "Current", "type": "Formula"}
      ]
    ids = ["doc1", "doc2"]
    
    db.add_documents(docs, metas, ids)
    
    # Query test
    results = db.similarity_search("How is voltage and current related in Ohm's law?", k=1)
    assert len(results) == 1
    doc, meta, score = results[0]
    assert "V = I * R" in doc
    assert meta["topic"] == "Current"
    assert score > 0.0

def test_retriever_formatting(temp_db_path):
    """Asserts retriever constructs properly formatted system context blocks."""
    db = JEEVectorStore(persist_directory=temp_db_path, collection_name="test_collection")
    retriever = JEERetriever(db_path=temp_db_path)
    
    # Retrieve context
    context = retriever.retrieve_context("Ohm's law resistance")
    assert "Ohm's law" in context
    assert "Reference #1" in context
