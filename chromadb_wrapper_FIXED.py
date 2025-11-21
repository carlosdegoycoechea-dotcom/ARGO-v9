"""
ARGO - ChromaDB Native Wrapper
Direct ChromaDB implementation without langchain dependencies
"""
import os
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

# Disable ChromaDB telemetry completely (BEFORE importing chromadb)
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_TELEMETRY'] = 'False'

import chromadb
from chromadb.config import Settings

from core.logger import get_logger

logger = get_logger("ChromaDBWrapper")


class Document:
    """Simple Document class to mimic langchain Document"""

    def __init__(self, page_content: str, metadata: Optional[Dict] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Document(page_content='{self.page_content[:50]}...', metadata={self.metadata})"


class ChromaDBVectorStore:
    """
    Native ChromaDB vector store implementation

    Provides a compatible interface with langchain's Chroma wrapper
    but uses ChromaDB directly to avoid dependency conflicts.
    """

    def __init__(
        self,
        persist_directory: str,
        embedding_function,
        collection_name: str = "default"
    ):
        """
        Initialize ChromaDB vector store

        Args:
            persist_directory: Path to persist database
            embedding_function: Embedding function (must have embed_query and embed_documents methods)
            collection_name: Name of the collection
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.embedding_function = embedding_function
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"ChromaDB initialized: {persist_directory}/{collection_name}")

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add texts to the vector store

        Args:
            texts: List of text strings
            metadatas: Optional list of metadata dicts
            ids: Optional list of IDs

        Returns:
            List of IDs
        """
        if not texts:
            return []

        # Generate embeddings
        embeddings = self.embedding_function.embed_documents(texts)

        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]

        # Prepare metadatas
        if metadatas is None:
            metadatas = [{} for _ in texts]

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        logger.debug(f"Added {len(texts)} texts to collection {self.collection_name}")
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Query string
            k: Number of results
            filter: Optional metadata filter

        Returns:
            List of Document objects
        """
        results = self.similarity_search_with_score(query, k=k, filter=filter)
        return [doc for doc, _ in results]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with scores

        Args:
            query: Query string
            k: Number of results
            filter: Optional metadata filter

        Returns:
            List of (Document, score) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_function.embed_query(query)

        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter,
            include=["documents", "metadatas", "distances"]
        )

        # Convert to Document objects with scores
        documents_with_scores = []

        if results['documents'] and len(results['documents']) > 0:
            for i, doc_text in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 1.0

                # Convert distance to similarity score (cosine: 1 - distance)
                # ChromaDB returns L2 distance, convert to similarity
                similarity = 1.0 / (1.0 + distance)

                doc = Document(page_content=doc_text, metadata=metadata)
                documents_with_scores.append((doc, similarity))

        return documents_with_scores

    def delete_collection(self):
        """Delete the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

    def get_collection_count(self) -> int:
        """Get number of items in collection"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0

    def persist(self):
        """
        Persist the database (no-op for PersistentClient)
        Included for compatibility with langchain interface
        """
        # PersistentClient auto-persists, so this is a no-op
        pass
