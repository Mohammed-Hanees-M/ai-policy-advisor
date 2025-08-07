import faiss
import numpy as np
from typing import List, Dict, Tuple
from src.models.embeddings import LegalEmbedder
import logging
# Import the new text splitter from langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorRetriever:
    """Manages the FAISS vector index for efficient semantic search."""
    def __init__(self):
        self.embedder = LegalEmbedder()
        self.index = None
        self.documents = []
        
    def build_index(self, documents: List[str]) -> None:
        """Creates a FAISS index from a list of document chunks."""
        if not documents:
            self.index = None
            logging.warning("No documents provided to build index.")
            return
            
        self.documents = documents
        logging.info(f"Embedding {len(documents)} document chunks...")
        embeddings = self.embedder.embed(documents)
        
        # Create a FAISS index
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings.astype(np.float32))
        logging.info("FAISS index built successfully.")
        
    def retrieve(
        self, 
        query: str, 
        k: int = 5, # Increased k to 5 for more context
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Retrieves the most relevant document chunks for a given query.
        """
        if self.index is None:
            logging.warning("Cannot retrieve, index is not built.")
            return []
            
        query_embedding = self.embedder.embed([query])
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        # Convert L2 distance to a similarity score (0-1 range)
        scores = 1 / (1 + distances[0])
        
        results = [
            (self.documents[idx], float(score))
            for idx, score in zip(indices[0], scores)
            if score >= threshold and idx < len(self.documents)
        ]
            
        return sorted(results, key=lambda x: x[1], reverse=True)

class DocumentProcessor:
    """
    Handles intelligent chunking of documents using semantic splitting.
    """
    def __init__(self):
        # This splitter tries to split on paragraphs, then sentences, then words.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # The target size for each chunk
            chunk_overlap=200,    # Overlap chunks to maintain context
            length_function=len,
        )
        
    def process(self, text: str, metadata: Dict) -> List[str]:
        """
        Processes a single document's text into meaningful chunks.

        Args:
            text: The full text of the document.
            metadata: A dictionary containing metadata (e.g., filename).

        Returns:
            A list of text chunks.
        """
        if not text:
            return []
        
        # The splitter automatically creates the context-aware chunks
        chunks = self.text_splitter.split_text(text)
        
        # Optional: Prepend metadata to each chunk for better context
        filename = metadata.get("name", "Unknown Document")
        return [f"From document '{filename}':\n{chunk}" for chunk in chunks]
