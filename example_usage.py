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
    
    # Specify collections to analyze
    # You can specify multiple collections like: ['abc', 'cde', 'errors']
    # Or set to None to auto-detect all error collections
    COLLECTIONS_TO_ANALYZE = ['abc', 'cde']  # Analyze both 'abc' and 'cde' collections
    
    # Optional: Limit number of documents per collection (useful for large datasets)
    # Set to None to analyze all documents
    DOCUMENT_LIMIT = None  # e.g., 10000 to limit to first 10k documents
    
    print("=" * 80)
    print("MongoDB Error Predictive Analytics")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Database: {DATABASE_NAME}")
    print(f"  Collections: {COLLECTIONS_TO_ANALYZE if COLLECTIONS_TO_ANALYZE else 'Auto-detect'}")
    print(f"  Document Limit: {DOCUMENT_LIMIT if DOCUMENT_LIMIT else 'All documents'}")
    print(f"  LLM Analysis: {'Enabled (Gemini)' if GEMINI_API_KEY else 'Disabled'}")
    print("\n" + "=" * 80 + "\n")
    
    # Create and run the analysis pipeline
    pipeline = ErrorAnalysisPipeline(
        connection_string=MONGODB_CONNECTION_STRING,
        database_name=DATABASE_NAME,
        gemini_api_key=GEMINI_API_KEY
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
