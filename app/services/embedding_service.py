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


# """
# Embedding service with Heroku optimization
# """

# import numpy as np
# import asyncio
# import logging
# from typing import List, Union
# import hashlib
# import json

# logger = logging.getLogger(__name__)

# class EmbeddingService:
#     """
#     Embedding service optimized for Heroku deployment
#     Falls back to mock embeddings if heavy ML libraries aren't available
#     """
    
#     def __init__(self):
#         self.model = None
#         self.use_mock = False
#         self.dimension = 384
        
#     async def initialize(self):
#         """Initialize the embedding service with fallbacks"""
#         try:
#             # Try to import sentence-transformers
#             from sentence_transformers import SentenceTransformer
            
#             logger.info("Loading sentence-transformers model...")
#             self.model = SentenceTransformer('all-MiniLM-L6-v2')
#             self.dimension = self.model.get_sentence_embedding_dimension()
#             logger.info(f"✅ Sentence transformer loaded (dim: {self.dimension})")
            
#         except ImportError:
#             logger.warning("sentence-transformers not available, trying transformers...")
            
#             try:
#                 from transformers import AutoTokenizer, AutoModel
#                 import torch
                
#                 logger.info("Loading transformers model...")
#                 self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
#                 self.transformer_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
#                 logger.info("✅ Transformers model loaded")
                
#             except (ImportError, Exception) as e:
#                 logger.warning(f"ML libraries not available ({e}), using mock embeddings")
#                 self.use_mock = True
                
#         except Exception as e:
#             logger.warning(f"Failed to load ML models ({e}), using mock embeddings")
#             self.use_mock = True
            
#         if self.use_mock:
#             logger.info("✅ Mock embedding service initialized for demo")
    
#     async def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
#         """Get embeddings for texts with fallback to mock"""
#         if isinstance(texts, str):
#             texts = [texts]
            
#         try:
#             if self.use_mock:
#                 return self._get_mock_embeddings(texts)
            
#             if self.model:
#                 # Use sentence-transformers
#                 embeddings = self.model.encode(texts, convert_to_numpy=True)
#                 return embeddings
                
#             elif hasattr(self, 'transformer_model'):
#                 # Use transformers directly
#                 return self._get_transformer_embeddings(texts)
            
#             else:
#                 return self._get_mock_embeddings(texts)
                
#         except Exception as e:
#             logger.error(f"Embedding generation failed: {e}")
#             return self._get_mock_embeddings(texts)
    
#     def _get_transformer_embeddings(self, texts: List[str]) -> np.ndarray:
#         """Get embeddings using transformers directly"""
#         try:
#             import torch
            
#             inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
            
#             with torch.no_grad():
#                 outputs = self.transformer_model(**inputs)
#                 embeddings = outputs.last_hidden_state.mean(dim=1)
                
#             return embeddings.numpy()
            
#         except Exception as e:
#             logger.error(f"Transformer embedding failed: {e}")
#             return self._get_mock_embeddings(texts)
    
#     def _get_mock_embeddings(self, texts: List[str]) -> np.ndarray:
#         """Generate deterministic mock embeddings for demo"""
#         embeddings = []
        
#         for text in texts:
#             # Create deterministic embedding based on text hash
#             text_hash = hashlib.md5(text.encode()).hexdigest()
            
#             # Convert hash to numbers and normalize
#             embedding = []
#             for i in range(0, len(text_hash), 2):
#                 val = int(text_hash[i:i+2], 16) / 255.0 - 0.5  # Normalize to [-0.5, 0.5]
#                 embedding.append(val)
            
#             # Extend or truncate to desired dimension
#             while len(embedding) < self.dimension:
#                 embedding.extend(embedding[:min(len(embedding), self.dimension - len(embedding))])
            
#             embedding = embedding[:self.dimension]
            
#             # Add some text-length based variation
#             length_factor = len(text) / 100.0
#             embedding = [e + (i % 2) * length_factor * 0.1 for i, e in enumerate(embedding)]
            
#             # Normalize to unit vector
#             norm = np.linalg.norm(embedding)
#             if norm > 0:
#                 embedding = [e / norm for e in embedding]
            
#             embeddings.append(embedding)
        
#         return np.array(embeddings, dtype=np.float32)
    
#     async def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
#         """Calculate cosine similarity between embeddings"""
#         try:
#             # Ensure embeddings are 1D
#             if embedding1.ndim > 1:
#                 embedding1 = embedding1.flatten()
#             if embedding2.ndim > 1:
#                 embedding2 = embedding2.flatten()
            
#             # Calculate cosine similarity
#             dot_product = np.dot(embedding1, embedding2)
#             norm1 = np.linalg.norm(embedding1)
#             norm2 = np.linalg.norm(embedding2)
            
#             if norm1 == 0 or norm2 == 0:
#                 return 0.0
            
#             similarity = dot_product / (norm1 * norm2)
#             return float(similarity)
            
#         except Exception as e:
#             logger.error(f"Similarity calculation failed: {e}")
#             return 0.0
    
#     def get_dimension(self) -> int:
#         """Get embedding dimension"""
#         return self.dimension
