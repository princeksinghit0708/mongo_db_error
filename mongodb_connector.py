"""
MongoDB Connector Module
Handles connection to MongoDB and data extraction from multiple collections
"""

from pymongo import MongoClient
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import schema system for generic column extraction
try:
    from collection_schema import collection_schema
    HAS_SCHEMA = True
except ImportError:
    HAS_SCHEMA = False
    logger.warning("Collection schema module not found. Using default extraction.")


class MongoDBConnector:
    """Class to handle MongoDB connections and data extraction"""
    
    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to connect to
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection_names(self) -> List[str]:
        """Get list of all collection names in the database"""
        try:
            collections = self.db.list_collection_names()
            logger.info(f"Found {len(collections)} collections: {collections}")
            return collections
        except Exception as e:
            logger.error(f"Error fetching collection names: {str(e)}")
            return []
    
    def read_collection(self, collection_name: str, query: Optional[Dict] = None, 
                       limit: Optional[int] = None) -> pd.DataFrame:
        """
        Read data from a MongoDB collection and convert to DataFrame
        
        Args:
            collection_name: Name of the collection to read
            query: Optional MongoDB query filter
            limit: Optional limit on number of documents to retrieve
            
        Returns:
            DataFrame containing the collection data
        """
        try:
            collection = self.db[collection_name]
            
            # Build query
            cursor = collection.find(query) if query else collection.find()
            
            if limit:
                cursor = cursor.limit(limit)
            
            # Convert to list
            data = list(cursor)
            
            if not data:
                logger.warning(f"No data found in collection: {collection_name}")
                return pd.DataFrame()
            
            # Use schema-based extraction if available, otherwise use default
            if HAS_SCHEMA and collection_schema.get_schema(collection_name):
                logger.info(f"Using schema-based extraction for {collection_name}")
                df = collection_schema.extract_columns(collection_name, data)
            else:
                # Default extraction (backward compatible)
                logger.info(f"Using default extraction for {collection_name}")
                df = pd.DataFrame(data)
                
                # Convert ObjectId to string for better handling
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                
                # Normalize nested structures (e.g., event.header, event.body)
                df = self._normalize_nested_structure(df, collection_name)
            
            # Convert timestamp to datetime if it exists
            timestamp_cols = ['timestamp', 'dataSavedAtTimeStamp', 'eventTransactionTime', 'transactionTime']
            for col in timestamp_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            logger.info(f"Successfully read {len(df)} documents from collection: {collection_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error reading collection {collection_name}: {str(e)}")
            return pd.DataFrame()
    
    def _normalize_nested_structure(self, df: pd.DataFrame, collection_name: str) -> pd.DataFrame:
        """
        Normalize nested MongoDB structures (e.g., event.header, event.body)
        Flattens nested objects and handles different collection structures
        
        Args:
            df: DataFrame with potentially nested structures
            collection_name: Name of the collection for context
            
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        # Handle event.header structure (for cde collection)
        if 'event' in df.columns:
            # Check if event is a dict-like structure
            if df['event'].dtype == 'object':
                # Try to extract header and body fields
                try:
                    event_series = df['event'].copy()
                    header_data = []
                    body_data = []
                    
                    for event in event_series:
                        if isinstance(event, dict):
                            header_data.append(event.get('header', {}))
                            body_data.append(event.get('body', {}))
                        else:
                            header_data.append({})
                            body_data.append({})
                    
                    # Flatten event.header
                    if any(header_data):
                        header_df = pd.json_normalize(header_data)
                        # Prefix header fields
                        header_df.columns = [f"header_{col}" if not col.startswith('header_') else col 
                                            for col in header_df.columns]
                        df = pd.concat([df.drop('event', axis=1), header_df], axis=1)
                    else:
                        df = df.drop('event', axis=1)
                    
                    # Flatten event.body
                    if any(body_data):
                        body_df = pd.json_normalize(body_data)
                        # Prefix body fields
                        body_df.columns = [f"body_{col}" if not col.startswith('body_') else col 
                                         for col in body_df.columns]
                        df = pd.concat([df, body_df], axis=1)
                except Exception as e:
                    logger.warning(f"Could not fully normalize event structure: {str(e)}")
                    # If normalization fails, try to keep event as-is or drop it
                    if 'event' in df.columns:
                        df = df.drop('event', axis=1)
        
        # Normalize error fields - map errorCode to errorType for consistency
        if 'errorCode' in df.columns and 'errorType' not in df.columns:
            df['errorType'] = df['errorCode']
            logger.info(f"Mapped 'errorCode' to 'errorType' for collection: {collection_name}")
        
        # Combine errorDetails with errorType if available
        if 'errorDetails' in df.columns and 'errorType' in df.columns:
            # Keep both, but errorType is primary
            df['errorMessage'] = df['errorDetails']
        
        # Normalize timestamp - use the most appropriate timestamp field
        if 'dataSavedAtTimeStamp' in df.columns and 'timestamp' not in df.columns:
            df['timestamp'] = df['dataSavedAtTimeStamp']
        elif 'eventTransactionTime' in df.columns and 'timestamp' not in df.columns:
            df['timestamp'] = df['eventTransactionTime']
        elif 'header_timestamp' in df.columns and 'timestamp' not in df.columns:
            df['timestamp'] = df['header_timestamp']
        
        return df
    
    def read_multiple_collections(self, collection_names: List[str], 
                                  query: Optional[Dict] = None,
                                  limit: Optional[int] = None) -> Dict[str, pd.DataFrame]:
        """
        Read data from multiple MongoDB collections
        
        Args:
            collection_names: List of collection names to read
            query: Optional MongoDB query filter
            limit: Optional limit on number of documents per collection
            
        Returns:
            Dictionary mapping collection names to DataFrames
        """
        data_dict = {}
        
        for collection_name in collection_names:
            df = self.read_collection(collection_name, query, limit)
            if not df.empty:
                # Add collection name as a column for tracking
                df['source_collection'] = collection_name
                data_dict[collection_name] = df
        
        logger.info(f"Successfully read {len(data_dict)} collections")
        return data_dict
    
    def get_error_collections(self, error_keyword: str = "error") -> Dict[str, pd.DataFrame]:
        """
        Automatically find and read collections that contain error data
        
        Args:
            error_keyword: Keyword to identify error-related collections
            
        Returns:
            Dictionary mapping collection names to DataFrames
        """
        collections = self.get_collection_names()
        error_collections = [col for col in collections if error_keyword.lower() in col.lower()]
        
        if not error_collections:
            # If no collections match keyword, try all collections
            logger.warning(f"No collections found with keyword '{error_keyword}'. Reading all collections.")
            error_collections = collections
        
        return self.read_multiple_collections(error_collections)
