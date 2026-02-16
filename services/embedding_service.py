"""
Embedding Service - Converts text to vector embeddings
Uses sentence-transformers library for semantic encoding
"""

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

# Load model once (cached in memory)
model = SentenceTransformer(EMBEDDING_MODEL)


def get_embedding(text: str) -> list[float]:
    """
    Convert text to embedding vector using pre-trained model.
    Uses normalize_embeddings=True to match how chunks were indexed
    (embed-chunks.py uses IndexFlatIP with normalized embeddings).
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the normalized embedding vector
    """
    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()  # Convert numpy array to list
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise
