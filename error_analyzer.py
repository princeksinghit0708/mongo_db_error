"""
Error Pattern Analysis Module
Analyzes error patterns, frequencies, and trends
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """Class to analyze error patterns and frequencies"""
    
    def __init__(self, data_dict: Dict[str, pd.DataFrame]):
        """
        Initialize with error data from multiple collections
        
        Args:
            data_dict: Dictionary mapping collection names to DataFrames
        """
        self.data_dict = data_dict
        self.combined_df = None
        self._combine_data()
    
    def _combine_data(self):
        """Combine all collection data into a single DataFrame"""
        if not self.data_dict:
            logger.warning("No data provided for analysis")
            return
        
        dfs = []
        for collection_name, df in self.data_dict.items():
            if not df.empty:
                dfs.append(df)
        
        if dfs:
            self.combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Combined {len(dfs)} collections into {len(self.combined_df)} total records")
        else:
            self.combined_df = pd.DataFrame()
            logger.warning("No valid data to combine")
    
    def get_error_type_frequency(self) -> pd.DataFrame:
        """Get frequency of each error type"""
        if self.combined_df is None or self.combined_df.empty:
            return pd.DataFrame()
        
        # Try to find error field (errorType or errorCode)
        error_col = None
        if 'errorType' in self.combined_df.columns:
            error_col = 'errorType'
        elif 'errorCode' in self.combined_df.columns:
            error_col = 'errorCode'
        
        if not error_col:
            logger.warning("'errorType' or 'errorCode' column not found in data")
            return pd.DataFrame()
        
        error_counts = self.combined_df[error_col].value_counts().reset_index()
        error_counts.columns = ['errorType', 'count']
        error_counts['percentage'] = (error_counts['count'] / error_counts['count'].sum() * 100).round(2)
        
        return error_counts
    
    def get_error_frequency_by_collection(self) -> pd.DataFrame:
        """Get error frequency grouped by collection"""
        if self.combined_df is None or self.combined_df.empty:
            return pd.DataFrame()
        
        if 'source_collection' not in self.combined_df.columns:
            logger.warning("'source_collection' column not found")
            return pd.DataFrame()
        
        # Find error field
        error_col = 'errorType' if 'errorType' in self.combined_df.columns else 'errorCode'
        if error_col not in self.combined_df.columns:
            logger.warning("'errorType' or 'errorCode' column not found")
            return pd.DataFrame()
        
        freq_df = self.combined_df.groupby(['source_collection', error_col]).size().reset_index(name='count')
        freq_df = freq_df.pivot(index=error_col, columns='source_collection', values='count').fillna(0)
        freq_df.index.name = 'errorType'
        
        return freq_df
    
    def get_temporal_analysis(self, time_column: str = 'timestamp') -> pd.DataFrame:
        """
        Analyze error patterns over time
        
        Args:
            time_column: Name of the timestamp column
            
        Returns:
            DataFrame with temporal error patterns
        """
        if self.combined_df is None or self.combined_df.empty:
            return pd.DataFrame()
        
        if time_column not in self.combined_df.columns:
            logger.warning(f"'{time_column}' column not found")
            return pd.DataFrame()
        
        if 'errorType' not in self.combined_df.columns:
            logger.warning("'errorType' column not found")
            return pd.DataFrame()
        
        # Ensure timestamp is datetime
        df = self.combined_df.copy()
        df[time_column] = pd.to_datetime(df[time_column])
        
        # Group by date and error type
        df['date'] = df[time_column].dt.date
        temporal_df = df.groupby(['date', 'errorType']).size().reset_index(name='count')
        
        # Add hour of day analysis
        df['hour'] = df[time_column].dt.hour
        hourly_df = df.groupby(['hour', 'errorType']).size().reset_index(name='count')
        
        return {
            'daily': temporal_df,
            'hourly': hourly_df
        }
    
    def get_error_patterns(self) -> Dict:
        """
        Extract various error patterns and statistics
        
        Returns:
            Dictionary containing various pattern analyses
        """
        if self.combined_df is None or self.combined_df.empty:
            return {}
        
        patterns = {}
        
        # Error type distribution
        patterns['error_type_frequency'] = self.get_error_type_frequency()
        
        # Collection-wise distribution
        patterns['collection_distribution'] = self.get_error_frequency_by_collection()
        
        # Temporal patterns
        patterns['temporal'] = self.get_temporal_analysis()
        
        # Type distribution (if 'type' column exists)
        if 'type' in self.combined_df.columns:
            patterns['type_distribution'] = self.combined_df['type'].value_counts().to_dict()
        
        # Business code distribution (for cde collection)
        if 'header_businessCode' in self.combined_df.columns:
            patterns['business_code_distribution'] = self.combined_df['header_businessCode'].value_counts().to_dict()
        
        # Domain distribution (for cde collection)
        if 'header_domain' in self.combined_df.columns:
            patterns['domain_distribution'] = self.combined_df['header_domain'].value_counts().to_dict()
        
        # Raw data length analysis (if rawData exists)
        if 'rawData' in self.combined_df.columns:
            self.combined_df['rawData_length'] = self.combined_df['rawData'].astype(str).str.len()
            patterns['rawData_length_stats'] = {
                'mean': self.combined_df['rawData_length'].mean(),
                'median': self.combined_df['rawData_length'].median(),
                'min': self.combined_df['rawData_length'].min(),
                'max': self.combined_df['rawData_length'].max(),
                'std': self.combined_df['rawData_length'].std()
            }
            
            # Length distribution by error type
            error_col = 'errorType' if 'errorType' in self.combined_df.columns else 'errorCode'
            if error_col in self.combined_df.columns:
                patterns['length_by_error'] = self.combined_df.groupby(error_col)['rawData_length'].describe()
        
        # Transaction amount analysis (for cde collection)
        if 'body_transactionAmount' in self.combined_df.columns:
            self.combined_df['body_transactionAmount'] = pd.to_numeric(
                self.combined_df['body_transactionAmount'], errors='coerce'
            )
            patterns['transaction_amount_stats'] = {
                'mean': self.combined_df['body_transactionAmount'].mean(),
                'median': self.combined_df['body_transactionAmount'].median(),
                'min': self.combined_df['body_transactionAmount'].min(),
                'max': self.combined_df['body_transactionAmount'].max(),
                'std': self.combined_df['body_transactionAmount'].std()
            }
        
        # Error co-occurrence (if multiple error types per record)
        error_col = 'errorType' if 'errorType' in self.combined_df.columns else 'errorCode'
        if error_col in self.combined_df.columns:
            patterns['unique_error_types'] = self.combined_df[error_col].nunique()
            patterns['total_errors'] = len(self.combined_df)
        
        return patterns
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of the error data"""
        if self.combined_df is None or self.combined_df.empty:
            return {}
        
        summary = {
            'total_records': len(self.combined_df),
            'collections_analyzed': len(self.data_dict),
            'date_range': {}
        }
        
        if 'timestamp' in self.combined_df.columns:
            df = self.combined_df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            summary['date_range'] = {
                'earliest': df['timestamp'].min().isoformat(),
                'latest': df['timestamp'].max().isoformat(),
                'span_days': (df['timestamp'].max() - df['timestamp'].min()).days
            }
        
        error_col = 'errorType' if 'errorType' in self.combined_df.columns else 'errorCode'
        if error_col in self.combined_df.columns:
            summary['error_types'] = {
                'count': self.combined_df[error_col].nunique(),
                'list': self.combined_df[error_col].unique().tolist()
            }
        
        return summary
