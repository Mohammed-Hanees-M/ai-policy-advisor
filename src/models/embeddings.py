from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging
import os
import hashlib
from pathlib import Path

class LegalEmbedder:
    def __init__(self):
        self.model = self._load_model()
        
    def _load_model(self):
        """Loads appropriate embedding model with fallback"""
        try:
            # Prefer a legal-specific model for better domain performance
            logging.info("Attempting to load 'nlpaueb/legal-bert-base-uncased' model...")
            model = SentenceTransformer('nlpaueb/legal-bert-base-uncased')
            logging.info("Successfully loaded Legal-BERT model.")
            return model
        except Exception as e:
            logging.warning(f"Legal-BERT model not found or failed to load: {e}. Falling back to a general-purpose model.")
            return SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed(
        self, 
        texts: Union[str, List[str]], 
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Generates normalized embeddings for a given text or list of texts.
        
        Args:
            texts: A single string or a list of strings to embed.
            batch_size: The batch size for encoding, for performance tuning.
            
        Returns:
            A numpy array of embeddings.
        """
        if isinstance(texts, str):
            texts = [texts]
            
        return self.model.encode(
            texts, 
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalize for cosine similarity
        )
    
    @property
    def dim(self) -> int:
        """Returns the embedding dimension size of the model."""
        return self.model.get_sentence_embedding_dimension()

class EmbeddingCache:
    """
    A persistent, file-based caching layer for text embeddings to avoid re-computation.
    """
    def __init__(self, embedder: LegalEmbedder, cache_dir: str = ".cache/embeddings"):
        self.embedder = embedder
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Retrieves an embedding from the cache or generates and saves a new one.

        Args:
            text: The text to get an embedding for.

        Returns:
            The numpy array for the embedding.
        """
        # Create a unique, stable filename from the hash of the text
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{text_hash}.npy"
        
        # 1. Check cache: If the file exists, load the embedding from it.
        if cache_file.exists():
            try:
                logging.info(f"Cache HIT for text hash: {text_hash[:10]}...")
                return np.load(cache_file)
            except Exception as e:
                logging.warning(f"Could not load cached file {cache_file}. Regenerating. Error: {e}")

        # 2. Cache miss: If the file doesn't exist, generate the embedding.
        logging.info(f"Cache MISS for text hash: {text_hash[:10]}.... Generating new embedding.")
        embedding = self.embedder.embed(text)
        
        # 3. Save the new embedding to the cache for future use.
        try:
            np.save(cache_file, embedding)
        except Exception as e:
            logging.error(f"Could not save cache file {cache_file}. Error: {e}")
            
        return embedding
