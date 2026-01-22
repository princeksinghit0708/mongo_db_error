"""
Collection Schema Configuration
Defines which columns to extract from each collection type
Makes the system generic and flexible for different JSON structures
"""

from typing import Dict, List, Optional, Callable
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class CollectionSchema:
    """Schema definition for extracting specific columns from collections"""
    
    def __init__(self):
        """Initialize with default schema configurations"""
        self.schemas = {}
        self._initialize_default_schemas()
    
    def _initialize_default_schemas(self):
        """Initialize default schema configurations for known collection types"""
        
        # Schema for "abc" collection (simple structure)
        self.schemas['abc'] = {
            'error_field': 'errorType',  # Primary error identifier
            'timestamp_field': 'timestamp',
            'required_fields': ['errorType', 'timestamp', 'rawData', 'type'],
            'optional_fields': ['uuid'],
            'extractors': {
                'errorType': lambda x: x.get('errorType', 'UNKNOWN'),
                'timestamp': lambda x: x.get('timestamp'),
                'rawData': lambda x: x.get('rawData', ''),
                'type': lambda x: x.get('type', ''),
                'uuid': lambda x: x.get('uuid', ''),
            }
        }
        
        # Schema for "cde" collection (nested structure)
        self.schemas['cde'] = {
            'error_field': 'errorCode',
            'timestamp_field': 'dataSavedAtTimeStamp',
            'required_fields': ['errorCode', 'errorDetails', 'timestamp', 'domain', 'businessCode'],
            'optional_fields': ['transactionAmount', 'merchantIdentifier'],
            'extractors': {
                'errorCode': lambda x: x.get('event', {}).get('header', {}).get('errorCode', 'UNKNOWN'),
                'errorDetails': lambda x: x.get('event', {}).get('header', {}).get('errorDetails', ''),
                'timestamp': lambda x: x.get('dataSavedAtTimeStamp') or x.get('event', {}).get('header', {}).get('timestamp'),
                'domain': lambda x: x.get('event', {}).get('header', {}).get('domain', ''),
                'businessCode': lambda x: x.get('event', {}).get('header', {}).get('businessCode', ''),
                'transactionAmount': lambda x: x.get('event', {}).get('body', {}).get('transactionAmount', ''),
                'merchantIdentifier': lambda x: x.get('event', {}).get('body', {}).get('merchantIdentifier', ''),
            }
        }
    
    def register_schema(self, collection_name: str, schema: Dict):
        """
        Register a custom schema for a collection
        
        Args:
            collection_name: Name of the collection
            schema: Dictionary with schema definition
                - error_field: Field name for error identifier
                - timestamp_field: Field name for timestamp
                - required_fields: List of required field names
                - optional_fields: List of optional field names
                - extractors: Dict of field_name -> extractor function
        """
        self.schemas[collection_name] = schema
        logger.info(f"Registered schema for collection: {collection_name}")
    
    def get_schema(self, collection_name: str) -> Optional[Dict]:
        """Get schema for a collection"""
        return self.schemas.get(collection_name)
    
    def extract_columns(self, collection_name: str, documents: List[Dict]) -> pd.DataFrame:
        """
        Extract only specified columns from documents based on schema
        
        Args:
            collection_name: Name of the collection
            documents: List of MongoDB documents
            
        Returns:
            DataFrame with only specified columns
        """
        schema = self.get_schema(collection_name)
        
        if not schema:
            logger.warning(f"No schema found for {collection_name}, using default extraction")
            return self._default_extraction(documents, collection_name)
        
        # Extract data using schema
        extracted_data = []
        
        for doc in documents:
            row = {}
            
            # Extract required fields
            for field in schema['required_fields']:
                if field in schema['extractors']:
                    row[field] = schema['extractors'][field](doc)
                else:
                    row[field] = None
            
            # Extract optional fields
            for field in schema.get('optional_fields', []):
                if field in schema['extractors']:
                    row[field] = schema['extractors'][field](doc)
            
            # Normalize error field name
            error_field = schema['error_field']
            if error_field != 'errorType' and error_field in row:
                row['errorType'] = row.pop(error_field)
            
            # Normalize timestamp field name
            timestamp_field = schema['timestamp_field']
            if timestamp_field != 'timestamp' and timestamp_field in row:
                row['timestamp'] = row.pop(timestamp_field)
            
            # Add source collection
            row['source_collection'] = collection_name
            
            extracted_data.append(row)
        
        df = pd.DataFrame(extracted_data)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        logger.info(f"Extracted {len(df)} records from {collection_name} with {len(df.columns)} columns")
        return df
    
    def _default_extraction(self, documents: List[Dict], collection_name: str) -> pd.DataFrame:
        """Default extraction when no schema is defined"""
        df = pd.DataFrame(documents)
        if not df.empty:
            df['source_collection'] = collection_name
        return df
    
    def get_all_columns(self) -> List[str]:
        """Get list of all columns used across all schemas"""
        all_columns = set(['source_collection', 'errorType', 'timestamp'])
        
        for schema in self.schemas.values():
            all_columns.update(schema.get('required_fields', []))
            all_columns.update(schema.get('optional_fields', []))
        
        return sorted(list(all_columns))


# Global schema instance
collection_schema = CollectionSchema()
