import pytest
import numpy as np
from src.utils.retrieval import VectorRetriever, DocumentStore
from src.models.embeddings import LegalEmbedder

@pytest.fixture
def sample_docs():
    return [
        "The LLC filing deadline is March 15 for most states",
        "OSHA requires safety training for all new employees",
        "Form 1099 must be filed by January 31 each year",
        "California minimum wage will increase to $16/hr in 2025"
    ]

@pytest.fixture
def retriever(sample_docs):
    retriever = VectorRetriever()
    retriever.build_index(sample_docs)
    return retriever

def test_build_index(retriever, sample_docs):
    assert retriever.index is not None
    assert retriever.index.ntotal == len(sample_docs)

def test_retrieve_exact_match(retriever):
    query = "When is the LLC filing deadline?"
    results = retriever.retrieve(query)
    assert len(results) > 0
    assert "March 15" in results[0][0]
    assert results[0][1] > 0.8  # High similarity score

def test_retrieve_no_match(retriever):
    query = "This is completely unrelated"
    results = retriever.retrieve(query, threshold=0.9)
    assert len(results) == 0

def test_retrieve_multiple_results(retriever):
    query = "employee requirements"
    results = retriever.retrieve(query, k=2)
    assert len(results) == 2
    assert any("OSHA" in r[0] for r in results)

def test_similarity_scores(retriever):
    query = "tax filing"
    results = retriever.retrieve(query)
    scores = [r[1] for r in results]
    assert sorted(scores, reverse=True) == scores  # Should be descending

def test_document_store_chunking():
    store = DocumentStore()
    long_text = "a " * 1000  # 1000-character text
    doc_id = store.add_document(long_text)
    assert len(store.docs[doc_id]["chunks"]) == 2  # Should split into 2 chunks

def test_empty_document_handling():
    retriever = VectorRetriever()
    with pytest.raises(ValueError):
        retriever.build_index([])

def test_embedding_consistency():
    embedder = LegalEmbedder()
    text = "Test embedding consistency"
    emb1 = embedder.embed([text])
    emb2 = embedder.embed([text])
    assert np.allclose(emb1, emb2, atol=1e-6)
