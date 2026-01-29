"""
Example usage script for analyzing MongoDB error collections
This example specifically targets the 'abc' collection mentioned in the requirements
"""

import os
from main import ErrorAnalysisPipeline

# Example configuration for your use case
if __name__ == "__main__":
    # MongoDB Configuration
    # Update these with your actual MongoDB connection details
    MONGODB_CONNECTION_STRING = os.getenv(
        'MONGODB_URI',
        'mongodb://localhost:27017/'  # Change to your MongoDB URI
    )
    
    DATABASE_NAME = os.getenv(
        'MONGODB_DATABASE',
        'your_database_name'  # Change to your database name
    )
    
    # Optional: Google Gemini API key for LLM-powered error analysis
    # Get your key from: https://makersuite.google.com/app/apikey
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
    
    # Data source: 'mongodb' = read MongoDB, store in SQLite, run pipeline from SQLite
    #             'sqlite' = load only from SQLite (run with 'mongodb' first to populate)
    DATA_SOURCE = os.getenv('DATA_SOURCE', 'mongodb')
    
    # Specify collections to analyze (used when DATA_SOURCE='mongodb')
    COLLECTIONS_TO_ANALYZE = ['abc', 'cde']
    DOCUMENT_LIMIT = None  # e.g., 10000 to limit documents per collection
    
    print("=" * 80)
    print("MongoDB Error Predictive Analytics")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Data source: {DATA_SOURCE} (pipeline uses SQLite for analysis when use_sqlite=True)")
    print(f"  Database: {DATABASE_NAME}")
    print(f"  Collections: {COLLECTIONS_TO_ANALYZE if DATA_SOURCE == 'mongodb' else 'N/A (loading from SQLite)'}")
    print(f"  Document Limit: {DOCUMENT_LIMIT if DOCUMENT_LIMIT else 'All documents'}")
    print(f"  LLM Analysis: {'Enabled (Gemini)' if GEMINI_API_KEY else 'Disabled'}")
    print("\n" + "=" * 80 + "\n")
    
    # Pipeline: use_sqlite=True means store in SQLite and run analysis from SQLite
    pipeline = ErrorAnalysisPipeline(
        connection_string=MONGODB_CONNECTION_STRING,
        database_name=DATABASE_NAME,
        gemini_api_key=GEMINI_API_KEY,
        use_sqlite=True,
        data_source=DATA_SOURCE
    )
    
    # Run the full analysis
    pipeline.run_full_analysis(
        collection_names=COLLECTIONS_TO_ANALYZE,
        limit=DOCUMENT_LIMIT
    )
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    print("\nCheck the 'output' directory for:")
    print("  - Visualizations (PNG files)")
    print("  - Analysis reports (JSON and TXT)")
    print("\n" + "=" * 80)
