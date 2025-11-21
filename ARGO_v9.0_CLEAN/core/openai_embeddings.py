"""
ARGO - Native OpenAI Embeddings Wrapper
Direct OpenAI API implementation without langchain dependencies
"""
from typing import List
from openai import OpenAI

from core.logger import get_logger

logger = get_logger("OpenAIEmbeddings")


class NativeOpenAIEmbeddings:
    """
    Native OpenAI embeddings implementation

    Provides a compatible interface with langchain's OpenAIEmbeddings
    but uses OpenAI API directly to avoid dependency conflicts.
    """

    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        """
        Initialize embeddings

        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key
        """
        self.model = model
        self.client = OpenAI(api_key=api_key)
        logger.info(f"OpenAI Embeddings initialized with model: {model}")

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating embedding for query: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            # OpenAI API can handle batches
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )

            # Extract embeddings in order
            embeddings = [item.embedding for item in response.data]
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings for documents: {e}")
            raise
