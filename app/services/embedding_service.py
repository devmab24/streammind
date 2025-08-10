"""
Embedding Service - Text to vector embeddings
"""

import asyncio
import numpy as np
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Text embedding generation service"""
    
    def __init__(self):
        self.model = None
        self.dimension = 384  # Default dimension
        self.model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self._embedding_cache = {}
        
    async def initialize(self):
        """Initialize embedding model"""
        try:
            # Try to load sentence-transformers model
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}")
                
                # Run model loading in thread to avoid blocking
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None, 
                    lambda: SentenceTransformer(self.model_name)
                )
                self.dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"✅ Embedding model loaded. Dimension: {self.dimension}")
                
            except ImportError:
                logger.warning("sentence-transformers not available, using mock embeddings")
                self.model = None
                self.dimension = 384
                
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            logger.info("Using mock embeddings for demo")
            self.model = None
            self.dimension = 384
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            # Check cache
            cache_key = hash(text)
            if cache_key in self._embedding_cache:
                return self._embedding_cache[cache_key]
            
            if self.model:
                # Use real model
                loop = asyncio.get_event_loop()
                embedding = await loop.run_in_executor(
                    None,
                    lambda: self.model.encode([text])[0]
                )
                embedding_list = embedding.tolist()
            else:
                # Use mock embedding for demo (deterministic based on text)
                embedding_list = self._generate_mock_embedding(text)
            
            # Cache result
            self._embedding_cache[cache_key] = embedding_list
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return self._generate_mock_embedding(text)
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if self.model:
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    None,
                    lambda: self.model.encode(texts)
                )
                return [emb.tolist() for emb in embeddings]
            else:
                # Mock embeddings
                return [self._generate_mock_embedding(text) for text in texts]
                
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding for demo purposes"""
        # Create pseudo-random but deterministic embedding based on text
        np.random.seed(abs(hash(text)) % (2**32))
        embedding = np.random.normal(0, 1, self.dimension)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors"""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        except Exception:
            return 0.0