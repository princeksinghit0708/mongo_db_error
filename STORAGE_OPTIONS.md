# Storage Options: Vector DB vs SQLite

## 🎯 When to Use What?

### Vector Database (ChromaDB)
**Best for:**
- ✅ Semantic search of error messages
- ✅ Finding similar errors across collections
- ✅ Error clustering and grouping
- ✅ Enhanced LLM context retrieval
- ✅ Similarity-based recommendations

**Use cases:**
- "Find errors similar to 'ENRICH_ERR_CCID_FRM_CLTIDLAST4CARDNUM'"
- "Group similar error patterns together"
- "What other errors have similar descriptions?"

### SQLite
**Best for:**
- ✅ Fast structured queries
- ✅ Aggregations and statistics
- ✅ Time-series analysis
- ✅ Traditional analytics
- ✅ Reporting and dashboards

**Use cases:**
- "Count errors by type per day"
- "Get all errors from collection 'abc' in last week"
- "Average transaction amount for errors"

### Recommendation: Use Both!
- **SQLite**: For structured analytics and reporting
- **Vector DB**: For semantic search and similarity analysis
- **MongoDB**: Source of truth (original data)

## 📊 Architecture with Both

```
MongoDB (Source)
    ↓
Schema-based Extraction (4-8 columns per collection)
    ↓
    ├──► SQLite (Structured Analytics)
    │    - Fast queries
    │    - Aggregations
    │    - Time-series
    │
    └──► Vector DB (Semantic Search)
         - Embeddings
         - Similarity search
         - Clustering
```

## 🔧 Implementation

### Option 1: SQLite Only (Recommended for Start)
```python
from sqlite_store import SQLiteStore

# Store errors
sqlite_store = SQLiteStore("./error_analytics.db")
sqlite_store.store_errors(combined_df)

# Query
summary = sqlite_store.get_error_summary()
```

### Option 2: Vector DB Only
```python
from vector_store import VectorStore

# Store with embeddings
vector_store = VectorStore(db_type="chroma")
vector_store.store_errors(combined_df)

# Search similar errors
similar = vector_store.search_similar_errors("enrichment error", n_results=5)
```

### Option 3: Both (Best of Both Worlds)
```python
from sqlite_store import SQLiteStore
from vector_store import VectorStore

# Store in both
sqlite_store = SQLiteStore()
sqlite_store.store_errors(combined_df)

vector_store = VectorStore(db_type="chroma")
vector_store.store_errors(combined_df)

# Use SQLite for analytics
summary = sqlite_store.get_error_summary()

# Use Vector DB for similarity
similar = vector_store.search_similar_errors("error query")
```

## 📝 Generic Schema System

### Benefits
1. **Extract only needed columns** (4-8 per collection)
2. **Handle different JSON structures** automatically
3. **Normalize field names** across collections
4. **Easy to add new collections** - just define schema

### Example Schema Definition

```python
from collection_schema import collection_schema

# Define schema for new collection
collection_schema.register_schema('new_collection', {
    'error_field': 'errorCode',
    'timestamp_field': 'created_at',
    'required_fields': ['errorCode', 'message', 'timestamp', 'severity'],
    'optional_fields': ['userId', 'sessionId'],
    'extractors': {
        'errorCode': lambda x: x.get('error', {}).get('code'),
        'message': lambda x: x.get('error', {}).get('message'),
        'timestamp': lambda x: x.get('created_at'),
        'severity': lambda x: x.get('level'),
        'userId': lambda x: x.get('user', {}).get('id'),
        'sessionId': lambda x: x.get('session', {}).get('id'),
    }
})
```

### Automatic Extraction
- Only extracts specified columns
- Handles nested JSON structures
- Normalizes field names
- Adds `source_collection` automatically

## 🚀 Performance Comparison

| Operation | SQLite | Vector DB | MongoDB |
|-----------|--------|-----------|---------|
| Structured Query | ⚡ Fast | ❌ Not for this | ⚡ Fast |
| Aggregation | ⚡ Fast | ❌ Not for this | ⚡ Fast |
| Semantic Search | ❌ No | ✅ Excellent | ❌ No |
| Similarity Search | ❌ No | ✅ Excellent | ❌ No |
| Clustering | ❌ No | ✅ Excellent | ❌ No |
| Storage Size | Small | Medium | Large |
| Setup Complexity | Low | Medium | Low |

## 💡 Recommendation

**For this project:**
1. **Start with SQLite** - Fast, simple, covers most analytics needs
2. **Add Vector DB later** - If you need semantic search or similarity analysis
3. **Use Schema System** - Makes it generic and maintainable

**Storage Strategy:**
- **SQLite**: Primary storage for analytics (recommended)
- **Vector DB**: Optional enhancement for semantic features
- **MongoDB**: Keep as source of truth, don't duplicate everything

## 📦 Installation

```bash
# For SQLite (built-in, no install needed)
# Already available with Python

# For Vector DB (optional)
pip install chromadb sentence-transformers
```

## 🔄 Migration Path

1. **Phase 1**: Use SQLite for structured storage
2. **Phase 2**: Add schema system for generic extraction
3. **Phase 3**: Add Vector DB for semantic search (if needed)
