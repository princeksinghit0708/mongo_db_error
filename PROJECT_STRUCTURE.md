# Complete Project Structure Guide

## 📁 Project Overview

This is a **MongoDB Error Predictive Analytics** system that:
- Reads errors from multiple MongoDB collections
- Analyzes error patterns and frequencies
- Uses ML models to predict errors
- Leverages LLM (Gemini) for intelligent error analysis
- Generates visualizations and reports
- Supports SQLite and Vector DB storage

---

## 📂 File Structure & Organization

```
Mongodb_error_predictive analysis/
│
├── 🚀 CORE MODULES (Main Functionality)
│   ├── main.py                    # Main pipeline orchestrator
│   ├── mongodb_connector.py       # MongoDB data extraction
│   ├── error_analyzer.py          # Error pattern analysis
│   ├── predictive_analytics.py    # ML models & LLM integration
│   ├── visualizer.py              # Chart generation
│   └── collection_schema.py       # Generic schema system
│
├── 💾 STORAGE MODULES (Data Persistence)
│   ├── sqlite_store.py            # SQLite storage
│   └── vector_store.py            # Vector DB for semantic search
│
├── 🤖 LLM MODULE
│   └── llm_prompts.py             # LLM prompt templates
│
├── 📝 EXAMPLES & USAGE
│   ├── example_usage.py           # Basic usage example
│   └── example_with_storage.py    # Example with storage options
│
├── 📚 DOCUMENTATION
│   ├── README.md                  # Main documentation
│   ├── QUICKSTART.md              # Quick start guide
│   ├── COLLECTION_STRUCTURES.md   # Collection format docs
│   ├── FLOW_DIAGRAM.md            # System flow explanation
│   ├── DATAFRAME_COMBINING.md     # How DataFrames are combined
│   ├── STORAGE_OPTIONS.md         # SQLite vs Vector DB guide
│   ├── ENHANCEMENTS_SUMMARY.md    # New features summary
│   ├── GITHUB_SETUP.md            # GitHub setup instructions
│   └── PROJECT_STRUCTURE.md       # This file
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt           # Python dependencies
│   ├── .gitignore                 # Git ignore rules
│   └── push_to_github.sh          # GitHub push script
│
└── 📊 OUTPUT (Generated)
    └── output/                    # Generated charts & reports
        ├── *.png                  # Visualization files
        ├── analysis_report.json   # JSON report
        └── analysis_report.txt    # Text report
```

---

## 🎯 Core Modules Explained

### 1. **main.py** - Pipeline Orchestrator
**Purpose**: Main entry point that coordinates all modules

**Key Class**: `ErrorAnalysisPipeline`

**Responsibilities**:
- Connects to MongoDB
- Orchestrates 7-step analysis pipeline
- Generates reports
- Manages storage (SQLite/Vector DB)

**How to Use**:
```python
from main import ErrorAnalysisPipeline

pipeline = ErrorAnalysisPipeline(
    connection_string="mongodb://...",
    database_name="my_db",
    gemini_api_key="...",
    use_sqlite=True,
    use_vector_db=False
)

pipeline.run_full_analysis(
    collection_names=['abc', 'cde'],
    limit=None
)
```

**When to Modify**: 
- To change pipeline flow
- To add new analysis steps
- To customize report generation

---

### 2. **mongodb_connector.py** - Data Extraction
**Purpose**: Handles MongoDB connections and data reading

**Key Class**: `MongoDBConnector`

**Responsibilities**:
- Establishes MongoDB connection
- Reads collections
- Normalizes nested structures
- Uses schema system for generic extraction

**Key Methods**:
- `connect()` - Connect to MongoDB
- `read_collection()` - Read single collection
- `read_multiple_collections()` - Read multiple collections
- `_normalize_nested_structure()` - Flatten nested JSON

**How to Use**:
```python
from mongodb_connector import MongoDBConnector

connector = MongoDBConnector("mongodb://...", "my_db")
connector.connect()
data_dict = connector.read_multiple_collections(['abc', 'cde'])
```

**When to Modify**:
- To change connection logic
- To add new normalization rules
- To customize data extraction

---

### 3. **error_analyzer.py** - Pattern Analysis
**Purpose**: Analyzes error patterns, frequencies, and trends

**Key Class**: `ErrorAnalyzer`

**Responsibilities**:
- Combines DataFrames from multiple collections
- Calculates error frequencies
- Analyzes temporal patterns
- Generates statistics

**Key Methods**:
- `get_error_type_frequency()` - Error counts
- `get_temporal_analysis()` - Time-based patterns
- `get_error_patterns()` - Comprehensive patterns
- `get_summary_statistics()` - Summary stats

**How to Use**:
```python
from error_analyzer import ErrorAnalyzer

analyzer = ErrorAnalyzer(data_dict)
patterns = analyzer.get_error_patterns()
summary = analyzer.get_summary_statistics()
```

**When to Modify**:
- To add new analysis metrics
- To change pattern detection logic
- To customize statistics

---

### 4. **predictive_analytics.py** - ML & LLM
**Purpose**: Machine learning predictions and LLM analysis

**Key Class**: `PredictiveAnalytics`

**Responsibilities**:
- Feature engineering
- ML model training (RF, GB, XGBoost)
- Future error predictions
- LLM-powered error analysis

**Key Methods**:
- `prepare_features()` - Feature engineering
- `train_error_prediction_model()` - Train ML models
- `predict_future_errors()` - 7-day predictions
- `predict_error_reason_llm()` - Gemini LLM analysis

**How to Use**:
```python
from predictive_analytics import PredictiveAnalytics

predictor = PredictiveAnalytics(df, gemini_api_key="...")
model_results = predictor.train_error_prediction_model()
future_errors = predictor.predict_future_errors(days_ahead=7)
llm_analysis = predictor.predict_error_reason_llm(error_record)
```

**When to Modify**:
- To add new ML models
- To change feature engineering
- To customize LLM prompts

---

### 5. **visualizer.py** - Charts & Dashboards
**Purpose**: Generates visualizations

**Key Class**: `ErrorVisualizer`

**Responsibilities**:
- Creates error frequency charts
- Generates temporal trend plots
- Builds collection distribution heatmaps
- Creates summary dashboards

**Key Methods**:
- `plot_error_frequency()` - Bar charts
- `plot_temporal_trends()` - Time series
- `plot_collection_distribution()` - Heatmaps
- `create_summary_dashboard()` - Combined dashboard

**How to Use**:
```python
from visualizer import ErrorVisualizer

visualizer = ErrorVisualizer(output_dir="output")
visualizer.plot_error_frequency(error_freq_df)
visualizer.create_summary_dashboard(patterns, model_results)
```

**When to Modify**:
- To change chart styles
- To add new visualizations
- To customize dashboard layout

---

### 6. **collection_schema.py** - Generic Schema System
**Purpose**: Defines which columns to extract from each collection

**Key Class**: `CollectionSchema`

**Responsibilities**:
- Defines schemas for collections
- Extracts only needed columns (4-8 per collection)
- Handles different JSON structures
- Normalizes field names

**How to Use**:
```python
from collection_schema import collection_schema

# Use existing schema
df = collection_schema.extract_columns('abc', documents)

# Register new schema
collection_schema.register_schema('new_collection', {
    'error_field': 'errorCode',
    'required_fields': ['errorCode', 'message', 'timestamp'],
    'extractors': {
        'errorCode': lambda x: x.get('error', {}).get('code'),
        # ...
    }
})
```

**When to Modify**:
- To add new collection types
- To change extracted columns
- To customize field extraction

---

## 💾 Storage Modules

### 7. **sqlite_store.py** - SQLite Storage
**Purpose**: Structured storage for fast queries

**Key Class**: `SQLiteStore`

**Use When**: You need fast structured queries and aggregations

**How to Use**:
```python
from sqlite_store import SQLiteStore

store = SQLiteStore("./error_analytics.db")
store.store_errors(df)
summary = store.get_error_summary()
```

---

### 8. **vector_store.py** - Vector DB Storage
**Purpose**: Semantic search and similarity analysis

**Key Class**: `VectorStore`

**Use When**: You need semantic search or error clustering

**How to Use**:
```python
from vector_store import VectorStore

store = VectorStore(db_type="chroma")
store.store_errors(df)
similar = store.search_similar_errors("enrichment error", n_results=5)
```

---

## 🤖 LLM Module

### 9. **llm_prompts.py** - Prompt Templates
**Purpose**: LLM prompt templates for error analysis

**Key Class**: `ErrorAnalysisPrompts`

**How to Use**:
```python
from llm_prompts import ErrorAnalysisPrompts

prompt = ErrorAnalysisPrompts.get_error_analysis_prompt(error_record)
```

**When to Modify**:
- To change LLM analysis focus
- To customize prompt structure
- To add new prompt types

---

## 📝 Example Files

### 10. **example_usage.py** - Basic Example
**Purpose**: Simple usage example

**Shows**: Basic pipeline setup without storage

---

### 11. **example_with_storage.py** - Advanced Example
**Purpose**: Example with SQLite and Vector DB

**Shows**: How to use storage options

---

## 🚀 How to Approach the Project

### Phase 1: Setup & Understanding
1. **Read Documentation**:
   - Start with `README.md`
   - Review `QUICKSTART.md`
   - Understand `FLOW_DIAGRAM.md`

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure**:
   - Set MongoDB connection in `example_usage.py`
   - Optionally set Gemini API key

### Phase 2: Basic Usage
1. **Run Basic Example**:
   ```bash
   python example_usage.py
   ```

2. **Review Output**:
   - Check `output/` directory
   - Review generated reports

3. **Understand Flow**:
   - Trace through `main.py`
   - See how modules interact

### Phase 3: Customization
1. **Add Collections**:
   - Define schema in `collection_schema.py`
   - Or use existing schemas

2. **Enable Storage**:
   - Use `example_with_storage.py`
   - Enable SQLite (recommended)
   - Optionally enable Vector DB

3. **Customize Analysis**:
   - Modify `error_analyzer.py` for new metrics
   - Adjust `predictive_analytics.py` for new models
   - Customize `visualizer.py` for new charts

### Phase 4: Advanced Features
1. **LLM Integration**:
   - Get Gemini API key
   - Customize prompts in `llm_prompts.py`

2. **Vector DB**:
   - Install: `pip install chromadb sentence-transformers`
   - Enable in pipeline
   - Use for semantic search

3. **Production Deployment**:
   - Set up environment variables
   - Configure logging
   - Schedule regular analysis

---

## 🔄 Typical Workflow

```
1. Configure MongoDB connection
   ↓
2. Define collection schemas (if needed)
   ↓
3. Run pipeline (main.py or example files)
   ↓
4. Review output (output/ directory)
   ↓
5. Query SQLite (if enabled) for analytics
   ↓
6. Use Vector DB (if enabled) for semantic search
   ↓
7. Iterate and customize
```

---

## 📊 Data Flow Summary

```
MongoDB Collections
    ↓
mongodb_connector.py (extracts data)
    ↓
collection_schema.py (normalizes to 4-8 columns)
    ↓
error_analyzer.py (combines & analyzes)
    ↓
    ├──► sqlite_store.py (structured storage)
    ├──► vector_store.py (embeddings)
    ├──► predictive_analytics.py (ML & LLM)
    └──► visualizer.py (charts)
    ↓
output/ (reports & visualizations)
```

---

## 🎯 Key Design Principles

1. **Modularity**: Each module has single responsibility
2. **Flexibility**: Schema system handles any JSON structure
3. **Extensibility**: Easy to add new collections, models, charts
4. **Performance**: SQLite for fast queries, Vector DB for semantic search
5. **Backward Compatible**: Works with existing code

---

## 💡 Best Practices

1. **Start Simple**: Use basic example first
2. **Add Storage Gradually**: SQLite first, Vector DB later
3. **Define Schemas**: For each collection type
4. **Extract Only Needed**: 4-8 columns per collection
5. **Review Output**: Check reports before customizing

---

## 🐛 Troubleshooting

**Issue**: Import errors
- **Solution**: `pip install -r requirements.txt`

**Issue**: MongoDB connection fails
- **Solution**: Check connection string and network

**Issue**: No data found
- **Solution**: Verify collection names and schema

**Issue**: Vector DB not working
- **Solution**: Install `chromadb` and `sentence-transformers`

---

## 📚 Documentation Files Reference

- **README.md**: Main documentation
- **QUICKSTART.md**: Quick start guide
- **FLOW_DIAGRAM.md**: System flow explanation
- **COLLECTION_STRUCTURES.md**: Collection format docs
- **STORAGE_OPTIONS.md**: SQLite vs Vector DB
- **ENHANCEMENTS_SUMMARY.md**: New features
- **DATAFRAME_COMBINING.md**: How DataFrames combine

---

## 🎓 Learning Path

1. **Beginner**: Read README → Run example_usage.py
2. **Intermediate**: Understand modules → Customize schemas
3. **Advanced**: Add storage → Integrate Vector DB → Customize ML models

---

This structure provides a complete, modular, and extensible system for MongoDB error analysis!
