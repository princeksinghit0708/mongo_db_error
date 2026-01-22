"""
Example with SQLite and Vector DB Storage Options
Shows how to use the enhanced storage capabilities
"""

import os
from main import ErrorAnalysisPipeline

if __name__ == "__main__":
    # MongoDB Configuration
    MONGODB_CONNECTION_STRING = os.getenv(
        'MONGODB_URI',
        'mongodb://localhost:27017/'
    )
    
    DATABASE_NAME = os.getenv('MONGODB_DATABASE', 'your_database_name')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
    
    # Storage Options
    USE_SQLITE = True   # Recommended: Fast structured queries
    USE_VECTOR_DB = False  # Optional: For semantic search
    
    # Collections to analyze
    COLLECTIONS_TO_ANALYZE = ['abc', 'cde']
    
    print("=" * 80)
    print("MongoDB Error Predictive Analytics with Storage Options")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Database: {DATABASE_NAME}")
    print(f"  Collections: {COLLECTIONS_TO_ANALYZE}")
    print(f"  SQLite Storage: {'Enabled' if USE_SQLITE else 'Disabled'}")
    print(f"  Vector DB Storage: {'Enabled' if USE_VECTOR_DB else 'Disabled'}")
    print(f"  LLM Analysis: {'Enabled (Gemini)' if GEMINI_API_KEY else 'Disabled'}")
    print("\n" + "=" * 80 + "\n")
    
    # Create pipeline with storage options
    pipeline = ErrorAnalysisPipeline(
        connection_string=MONGODB_CONNECTION_STRING,
        database_name=DATABASE_NAME,
        gemini_api_key=GEMINI_API_KEY,
        use_sqlite=USE_SQLITE,
        use_vector_db=USE_VECTOR_DB
    )
    
    # Run analysis
    pipeline.run_full_analysis(
        collection_names=COLLECTIONS_TO_ANALYZE,
        limit=None
    )
    
    # Example: Query from SQLite
    if USE_SQLITE and pipeline.sqlite_store:
        print("\n" + "=" * 80)
        print("SQLite Query Example")
        print("=" * 80)
        summary = pipeline.sqlite_store.get_error_summary()
        print(f"Total errors in SQLite: {summary['total_errors']}")
        print(f"Errors by type: {summary['errors_by_type']}")
    
    # Example: Semantic search from Vector DB
    if USE_VECTOR_DB and pipeline.vector_store:
        print("\n" + "=" * 80)
        print("Vector DB Semantic Search Example")
        print("=" * 80)
        similar = pipeline.vector_store.search_similar_errors(
            "enrichment error", 
            n_results=3
        )
        print(f"Found {len(similar)} similar errors")
        for error in similar:
            print(f"  - {error['metadata'].get('errorType', 'Unknown')}")
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
