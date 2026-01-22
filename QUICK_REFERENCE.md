# Quick Reference Guide

## 📋 File Quick Reference

| File | Purpose | When to Use | Key Class/Function |
|------|---------|-------------|-------------------|
| **main.py** | Pipeline orchestrator | Always (entry point) | `ErrorAnalysisPipeline` |
| **mongodb_connector.py** | MongoDB data extraction | Always | `MongoDBConnector` |
| **error_analyzer.py** | Pattern analysis | Always | `ErrorAnalyzer` |
| **predictive_analytics.py** | ML & LLM | Always | `PredictiveAnalytics` |
| **visualizer.py** | Charts generation | Always | `ErrorVisualizer` |
| **collection_schema.py** | Generic extraction | When adding collections | `CollectionSchema` |
| **sqlite_store.py** | SQLite storage | Optional (recommended) | `SQLiteStore` |
| **vector_store.py** | Vector DB storage | Optional (semantic search) | `VectorStore` |
| **llm_prompts.py** | LLM prompts | When using LLM | `ErrorAnalysisPrompts` |
| **example_usage.py** | Basic example | Learning/Testing | - |
| **example_with_storage.py** | Advanced example | With storage | - |

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run basic example
python example_usage.py

# 3. Run with storage
python example_with_storage.py

# 4. Check output
ls output/
```

## 📝 Common Tasks

### Task 1: Analyze Collections
```python
from main import ErrorAnalysisPipeline

pipeline = ErrorAnalysisPipeline(
    connection_string="mongodb://localhost:27017/",
    database_name="my_db"
)
pipeline.run_full_analysis(collection_names=['abc', 'cde'])
```

### Task 2: Add New Collection Schema
```python
from collection_schema import collection_schema

collection_schema.register_schema('new_collection', {
    'error_field': 'errorCode',
    'required_fields': ['errorCode', 'message', 'timestamp'],
    'extractors': {
        'errorCode': lambda x: x.get('error', {}).get('code'),
        'message': lambda x: x.get('error', {}).get('message'),
        'timestamp': lambda x: x.get('created_at'),
    }
})
```

### Task 3: Query SQLite
```python
from sqlite_store import SQLiteStore

store = SQLiteStore()
summary = store.get_error_summary()
print(summary)
```

### Task 4: Semantic Search
```python
from vector_store import VectorStore

store = VectorStore(db_type="chroma")
similar = store.search_similar_errors("enrichment error", n_results=5)
```

## 🎯 Module Flow

```
main.py
  ├──► mongodb_connector.py → data
  ├──► error_analyzer.py → patterns
  ├──► predictive_analytics.py → predictions
  ├──► visualizer.py → charts
  ├──► sqlite_store.py → storage (optional)
  └──► vector_store.py → embeddings (optional)
```

## 📚 Documentation Files

- **PROJECT_STRUCTURE.md** - Complete file structure
- **ARCHITECTURE.md** - System architecture
- **FLOW_DIAGRAM.md** - Data flow
- **STORAGE_OPTIONS.md** - Storage guide
- **QUICKSTART.md** - Quick start
- **README.md** - Main docs

## 🔧 Configuration

### MongoDB Connection
```python
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "your_database"
```

### Collections
```python
COLLECTIONS_TO_ANALYZE = ['abc', 'cde']
```

### Storage Options
```python
use_sqlite=True      # Recommended
use_vector_db=False  # Optional
```

### LLM (Optional)
```python
gemini_api_key="your_key_here"
```

## 📊 Output Files

All outputs go to `output/` directory:
- `error_frequency.png` - Error counts
- `temporal_trends.png` - Time trends
- `model_performance.png` - ML accuracy
- `summary_dashboard.png` - Combined view
- `analysis_report.json` - JSON report
- `analysis_report.txt` - Text report

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| MongoDB connection fails | Check connection string |
| No data found | Verify collection names |
| Vector DB not working | Install `chromadb sentence-transformers` |

## 💡 Pro Tips

1. **Start with SQLite** - Covers 90% of use cases
2. **Define schemas** - Makes it generic
3. **Extract only needed** - 4-8 columns per collection
4. **Review output** - Check reports before customizing
5. **Use examples** - Start with `example_usage.py`

---

**Need more details?** Check `PROJECT_STRUCTURE.md` and `ARCHITECTURE.md`
