"""
Vector Database Integration
Stores error embeddings for semantic search and similarity analysis
Supports multiple vector DB backends (Chroma, Pinecone, etc.)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import vector DB libraries
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    logger.warning("ChromaDB not installed. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("SentenceTransformers not installed. Install with: pip install sentence-transformers")


class VectorStore:
    """Vector database for storing and searching error embeddings"""
    
    def __init__(self, db_type: str = "chroma", persist_directory: str = "./vector_db"):
        """
        Initialize vector store
        
        Args:
            db_type: Type of vector DB ("chroma", "sqlite", or None)
            persist_directory: Directory to persist vector DB
        """
        self.db_type = db_type
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        if db_type == "chroma" and HAS_CHROMA:
            self._init_chroma()
        elif db_type == "sqlite":
            logger.info("SQLite mode - using SQLite for structured storage")
        else:
            logger.warning(f"Vector DB type '{db_type}' not available or not installed")
    
    def _init_chroma(self):
        """Initialize ChromaDB"""
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="error_embeddings",
                metadata={"description": "MongoDB error embeddings for semantic search"}
            )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
    
    def _init_embedding_model(self):
        """Initialize embedding model"""
        if not HAS_SENTENCE_TRANSFORMERS:
            logger.warning("SentenceTransformers not available. Cannot generate embeddings.")
            return None
        
        try:
            # Use a lightweight, fast model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded: all-MiniLM-L6-v2")
            return self.embedding_model
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            return None
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for text data
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings
        """
        if not self.embedding_model:
            self._init_embedding_model()
        
        if not self.embedding_model:
            raise ValueError("Embedding model not available")
        
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def store_errors(self, df: pd.DataFrame, error_text_fields: List[str] = None):
        """
        Store error records in vector DB
        
        Args:
            df: DataFrame with error records
            error_text_fields: List of column names to use for embedding text
        """
        if self.db_type != "chroma" or not self.client:
            logger.warning("Vector DB not initialized. Skipping vector storage.")
            return
        
        if error_text_fields is None:
            error_text_fields = ['errorType', 'errorDetails', 'errorMessage']
        
        # Combine text fields for embedding
        texts = []
        metadata_list = []
        ids = []
        
        for idx, row in df.iterrows():
            # Combine relevant text fields
            text_parts = []
            for field in error_text_fields:
                if field in row and pd.notna(row[field]):
                    text_parts.append(str(row[field]))
            
            combined_text = " | ".join(text_parts)
            texts.append(combined_text)
            
            # Store metadata
            metadata = {
                'errorType': str(row.get('errorType', 'UNKNOWN')),
                'source_collection': str(row.get('source_collection', '')),
                'timestamp': str(row.get('timestamp', '')),
            }
            
            # Add other fields as metadata
            for col in df.columns:
                if col not in ['errorType', 'source_collection', 'timestamp']:
                    if pd.notna(row[col]):
                        metadata[col] = str(row[col])[:100]  # Limit length
            
            metadata_list.append(metadata)
            ids.append(f"{row.get('source_collection', 'unknown')}_{idx}")
        
        # Create embeddings
        logger.info(f"Creating embeddings for {len(texts)} error records...")
        embeddings = self.create_embeddings(texts)
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadata_list,
            ids=ids
        )
        
        logger.info(f"Stored {len(texts)} error embeddings in vector DB")
    
    def search_similar_errors(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Search for similar errors using semantic similarity
        
        Args:
            query_text: Text to search for
            n_results: Number of similar results to return
            
        Returns:
            List of similar error records
        """
        if self.db_type != "chroma" or not self.client:
            logger.warning("Vector DB not initialized. Cannot search.")
            return []
        
        # Create query embedding
        query_embedding = self.create_embeddings([query_text])[0]
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        # Format results
        similar_errors = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                similar_errors.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return similar_errors
    
    def get_error_clusters(self, df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
        """
        Cluster similar errors using embeddings
        
        Args:
            df: DataFrame with error records
            n_clusters: Number of clusters
            
        Returns:
            DataFrame with cluster assignments
        """
        from sklearn.cluster import KMeans
        
        # Create embeddings for all errors
        error_texts = []
        for idx, row in df.iterrows():
            text = f"{row.get('errorType', '')} {row.get('errorDetails', '')} {row.get('errorMessage', '')}"
            error_texts.append(text)
        
        embeddings = self.create_embeddings(error_texts)
        
        # Cluster
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        
        df_with_clusters = df.copy()
        df_with_clusters['error_cluster'] = clusters
        
        return df_with_clusters
