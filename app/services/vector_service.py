"""
Vector Search Service - Searches FAISS index for similar chunks
Uses pre-built FAISS index with all chunk embeddings
"""

import faiss
import json
import numpy as np
from app.core.config import FAISS_INDEX_PATH, ID_TO_CHUNK_PATH, TOP_K, SIMILARITY_THRESHOLD

# the embedding model is defined in embedding_service; vector service
# can leverage it for convenience when encoding text before searching.
from app.services.embedding_service import model as embedding_model
from app.services.embedding_service import get_embedding


class VectorSearchService:
    """Service for searching similar chunks using FAISS"""

    def __init__(self):
        """Initialize FAISS index and chunk metadata"""
        try:
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(ID_TO_CHUNK_PATH, 'r') as f:
                self.id_to_chunk = json.load(f)
            print(f"✓ Loaded FAISS index with {self.index.ntotal} chunks")
        except Exception as e:
            print(f"Error loading FAISS index: {str(e)}")
            raise

    def search_similar_chunks(self, query_embedding: list[float]) -> list[dict]:
        """
        Find top-K most similar chunks to query embedding

        Args:
            query_embedding: Vector representation of the question

        Returns:
            List of similar chunks with metadata and similarity scores
        """
        try:
            # Convert to numpy and reshape for FAISS
            query_vector = np.array([query_embedding], dtype=np.float32)

            # Search FAISS index
            distances, indices = self.index.search(query_vector, k=TOP_K)

            # Get chunks from mapping and filter by threshold
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if distance >= SIMILARITY_THRESHOLD:
                    chunk = self.id_to_chunk[str(idx)].copy()
                    chunk['similarity_score'] = float(distance)
                    results.append(chunk)

            return results
        except Exception as e:
            print(f"Error searching FAISS index: {str(e)}")
            raise


# Initialize service globally (lazy-loaded)
_vector_service = None

def get_vector_service():
    """Lazy load vector search service"""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorSearchService()
    return _vector_service

def search_similar_chunks(query_embedding: list[float]) -> list[dict]:
    """Convenience function to search similar chunks"""
    return get_vector_service().search_similar_chunks(query_embedding)

def embed_text(text: str) -> np.ndarray:
    """Helper to encode text using the shared sentence‑transformer model.

    This is mostly for backwards compatibility/utility; other code should
    preferably call :func:`get_embedding` since it handles list output and
    normalization. The returned array is **not** normalized (caller may want to
    set ``normalize_embeddings=True`` when passing to FAISS).
    """
    # use the imported model from embedding_service
    return embedding_model.encode([text], normalize_embeddings=False)[0]