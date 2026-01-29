"""
SQLite Storage for Error Data
Provides structured storage and fast querying for error analytics
"""

import sqlite3
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLiteStore:
    """SQLite database for storing error data"""
    
    def __init__(self, db_path: str = "./error_analytics.db"):
        """
        Initialize SQLite store
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish SQLite connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {str(e)}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Main errors table (columns aligned with pipeline/schema output)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_collection TEXT NOT NULL,
                errorType TEXT,
                errorCode TEXT,
                errorDetails TEXT,
                errorMessage TEXT,
                timestamp TEXT,
                rawData TEXT,
                type TEXT,
                domain TEXT,
                businessCode TEXT,
                transactionAmount REAL,
                merchantIdentifier TEXT,
                uuid TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # SQLite: create indexes separately
        for idx_name, col in [("idx_errors_errorType", "errorType"),
                              ("idx_errors_source_collection", "source_collection"),
                              ("idx_errors_timestamp", "timestamp")]:
            try:
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_name} ON errors ({col})"
                )
            except sqlite3.OperationalError:
                pass
        
        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT,
                result_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Model predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                errorType TEXT,
                predicted_count REAL,
                prediction_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        logger.info("SQLite tables created/verified")
    
    def get_table_columns(self, table_name: str = "errors") -> List[str]:
        """Get list of column names for a table (excluding id, created_at for inserts)."""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall() if row[1] not in ("id",)]
    
    def store_errors(self, df: pd.DataFrame, table_name: str = "errors"):
        """
        Store error DataFrame in SQLite. Only columns that exist in the table are stored.
        
        Args:
            df: DataFrame with error records
            table_name: Name of table to store in
        """
        if df.empty:
            logger.warning("Empty DataFrame, nothing to store")
            return
        
        try:
            table_cols = self.get_table_columns(table_name)
            # Keep only columns that exist in the table and in the DataFrame
            cols_to_store = [c for c in df.columns if c in table_cols]
            if not cols_to_store:
                logger.warning("No columns from DataFrame match the errors table. Check schema.")
                return
            
            df_to_store = df[cols_to_store].copy()
            
            # Convert timestamp to string for SQLite
            if 'timestamp' in df_to_store.columns:
                df_to_store['timestamp'] = pd.to_datetime(
                    df_to_store['timestamp'], errors='coerce'
                ).astype(str)
            
            df_to_store.to_sql(table_name, self.conn, if_exists='append', index=False)
            logger.info(f"Stored {len(df_to_store)} records in SQLite table '{table_name}'")
        except Exception as e:
            logger.error(f"Failed to store errors in SQLite: {str(e)}")
            raise
    
    def load_all_errors(self, table_name: str = "errors") -> pd.DataFrame:
        """
        Load all error records from SQLite into a DataFrame for the pipeline.
        
        Returns:
            DataFrame with all errors; timestamp column is parsed back to datetime.
        """
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            # Drop SQLite-only columns for pipeline compatibility
            for drop in ("id", "created_at"):
                if drop in df.columns:
                    df = df.drop(columns=[drop])
            # Parse timestamp for analysis
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            logger.info(f"Loaded {len(df)} error records from SQLite")
            return df
        except Exception as e:
            logger.error(f"Failed to load errors from SQLite: {str(e)}")
            return pd.DataFrame()
    
    def query_errors(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Query errors from SQLite
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            DataFrame with query results
        """
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            return df
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return pd.DataFrame()
    
    def get_error_summary(self) -> Dict:
        """Get summary statistics from SQLite"""
        summary = {}
        
        # Total errors
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM errors")
        summary['total_errors'] = cursor.fetchone()[0]
        
        # Errors by type
        cursor.execute("""
            SELECT errorType, COUNT(*) as count 
            FROM errors 
            WHERE errorType IS NOT NULL
            GROUP BY errorType 
            ORDER BY count DESC
        """)
        summary['errors_by_type'] = dict(cursor.fetchall())
        
        # Errors by collection
        cursor.execute("""
            SELECT source_collection, COUNT(*) as count 
            FROM errors 
            GROUP BY source_collection
        """)
        summary['errors_by_collection'] = dict(cursor.fetchall())
        
        return summary
    
    def close(self):
        """Close SQLite connection"""
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed")
