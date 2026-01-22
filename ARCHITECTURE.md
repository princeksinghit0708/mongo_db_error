# System Architecture & File Relationships

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRY POINTS                                   │
├─────────────────────────────────────────────────────────────────┤
│  example_usage.py          example_with_storage.py              │
│  (Basic)                   (With SQLite/Vector DB)              │
└──────────────────────┬──────────────────────┬─────────────────────┘
                      │                      │
                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN ORCHESTRATOR                             │
│                    main.py                                       │
│                    ErrorAnalysisPipeline                         │
└──────┬───────────────┬───────────────┬───────────────┬──────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   DATA       │ │   ANALYSIS   │ │   ML/LLM     │ │  VISUALIZE   │
│ EXTRACTION   │ │               │ │              │ │              │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│mongodb_      │ │error_        │ │predictive_   │ │visualizer.py │
│connector.py  │ │analyzer.py   │ │analytics.py  │ │              │
│              │ │              │ │              │ │              │
│• Connect     │ │• Combine     │ │• Features    │ │• Charts      │
│• Read        │ │• Patterns    │ │• ML Models  │ │• Dashboards  │
│• Normalize   │ │• Frequency   │ │• Predictions │ │• Reports     │
│• Schema      │ │• Temporal    │ │• LLM Analysis│ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPPORTING MODULES                            │
├─────────────────────────────────────────────────────────────────┤
│  collection_schema.py  │  llm_prompts.py  │  Storage Modules    │
│  • Schema definitions   │  • Prompt        │  • sqlite_store.py  │
│  • Column extraction    │    templates     │  • vector_store.py  │
│  • Field normalization  │  • LLM config    │                     │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT                                         │
│                    output/ directory                              │
│  • Charts (PNG)  • Reports (JSON/TXT)  • SQLite DB  • Vector DB │
└─────────────────────────────────────────────────────────────────┘
```

## 🔗 File Dependencies

### Core Dependency Chain

```
example_usage.py
    └──► main.py
            ├──► mongodb_connector.py
            │       └──► collection_schema.py (optional)
            │
            ├──► error_analyzer.py
            │       └──► (uses data from mongodb_connector)
            │
            ├──► predictive_analytics.py
            │       ├──► llm_prompts.py (for LLM)
            │       └──► (uses data from error_analyzer)
            │
            ├──► visualizer.py
            │       └──► (uses data from error_analyzer & predictive_analytics)
            │
            ├──► sqlite_store.py (optional)
            │       └──► (stores data from error_analyzer)
            │
            └──► vector_store.py (optional)
                    └──► (stores embeddings from error_analyzer)
```

## 📦 Module Categories

### 1. **Data Layer** (Bottom)
```
mongodb_connector.py
    ↓ Reads from MongoDB
collection_schema.py
    ↓ Normalizes/extracts columns
```

### 2. **Analysis Layer** (Middle)
```
error_analyzer.py
    ↓ Analyzes patterns
predictive_analytics.py
    ↓ ML & LLM analysis
```

### 3. **Storage Layer** (Parallel)
```
sqlite_store.py      (Structured storage)
vector_store.py      (Semantic storage)
```

### 4. **Presentation Layer** (Top)
```
visualizer.py        (Charts)
main.py              (Reports)
```

### 5. **Configuration Layer** (Supporting)
```
llm_prompts.py       (LLM prompts)
collection_schema.py (Schema definitions)
```

## 🔄 Execution Flow

### Step-by-Step File Execution

```
1. User runs: example_usage.py
   │
   ├──► Imports: main.py
   │
2. main.py: ErrorAnalysisPipeline.__init__()
   │
   ├──► Creates: MongoDBConnector (mongodb_connector.py)
   ├──► Creates: ErrorVisualizer (visualizer.py)
   ├──► Optionally: SQLiteStore (sqlite_store.py)
   └──► Optionally: VectorStore (vector_store.py)
   │
3. main.py: run_full_analysis()
   │
   ├──► Step 1: connector.connect() → mongodb_connector.py
   │
   ├──► Step 2: connector.read_multiple_collections()
   │       │
   │       ├──► Uses: collection_schema.py (if available)
   │       └──► Returns: data_dict
   │
   ├──► Step 3: ErrorAnalyzer(data_dict) → error_analyzer.py
   │       │
   │       └──► Returns: patterns, summary
   │
   ├──► Step 3.5: Store in SQLite/Vector DB (if enabled)
   │       │
   │       ├──► sqlite_store.py: store_errors()
   │       └──► vector_store.py: store_errors()
   │
   ├──► Step 4: PredictiveAnalytics(df) → predictive_analytics.py
   │       │
   │       ├──► Uses: llm_prompts.py (for LLM)
   │       └──► Returns: model_results, predictions
   │
   ├──► Step 5: LLM Analysis
   │       │
   │       ├──► Uses: llm_prompts.py
   │       └──► Uses: predictive_analytics.py
   │
   ├──► Step 6: Generate Visualizations
   │       │
   │       └──► visualizer.py: plot_*()
   │
   └──► Step 7: Generate Reports
           │
           └──► main.py: _generate_report()
                   │
                   └──► Saves to: output/
```

## 🎯 Module Responsibilities Matrix

| Module | Reads From | Writes To | Used By |
|--------|-----------|-----------|---------|
| `mongodb_connector.py` | MongoDB | DataFrame | `main.py` |
| `collection_schema.py` | MongoDB docs | DataFrame | `mongodb_connector.py` |
| `error_analyzer.py` | DataFrame | Analysis dicts | `main.py` |
| `predictive_analytics.py` | DataFrame | Predictions, LLM | `main.py` |
| `llm_prompts.py` | Error records | Prompts | `predictive_analytics.py` |
| `visualizer.py` | Analysis data | PNG files | `main.py` |
| `sqlite_store.py` | DataFrame | SQLite DB | `main.py` |
| `vector_store.py` | DataFrame | Vector DB | `main.py` |
| `main.py` | All modules | Reports, output/ | `example_*.py` |

## 🔧 Configuration Files

### Runtime Configuration
- **`example_usage.py`**: Basic configuration
- **`example_with_storage.py`**: Advanced configuration
- **Environment variables**: `.env` file (optional)

### Schema Configuration
- **`collection_schema.py`**: Collection schemas
- Can be extended at runtime

### LLM Configuration
- **`llm_prompts.py`**: Prompt templates
- Can be customized

## 📊 Data Flow Between Modules

```
MongoDB
  ↓ (pymongo)
mongodb_connector.py
  ↓ (DataFrame)
collection_schema.py (optional normalization)
  ↓ (Normalized DataFrame)
error_analyzer.py
  ↓ (Combined DataFrame)
  ├──► sqlite_store.py (structured)
  ├──► vector_store.py (embeddings)
  └──► predictive_analytics.py
        ↓ (Features)
        ├──► ML Models
        └──► LLM (via llm_prompts.py)
              ↓
visualizer.py
  ↓ (Charts)
main.py (_generate_report)
  ↓
output/ directory
```

## 🚀 Getting Started Path

### Path 1: Quick Start (Beginner)
```
1. Read: README.md
2. Run: example_usage.py
3. Review: output/ directory
```

### Path 2: With Storage (Intermediate)
```
1. Read: STORAGE_OPTIONS.md
2. Run: example_with_storage.py
3. Query: SQLite database
```

### Path 3: Custom Schema (Advanced)
```
1. Read: COLLECTION_STRUCTURES.md
2. Modify: collection_schema.py
3. Run: Custom analysis
```

### Path 4: Full Customization (Expert)
```
1. Understand: All modules
2. Customize: Each module as needed
3. Extend: Add new features
```

## 💡 Key Insights

1. **`main.py` is the orchestrator** - Everything flows through it
2. **`mongodb_connector.py` is the data source** - All data starts here
3. **`collection_schema.py` makes it generic** - Handles any structure
4. **Storage modules are optional** - Add as needed
5. **All modules are independent** - Can modify one without breaking others

## 🔍 File Modification Guide

### To Add New Collection Type:
→ Modify: `collection_schema.py`

### To Add New Analysis Metric:
→ Modify: `error_analyzer.py`

### To Add New ML Model:
→ Modify: `predictive_analytics.py`

### To Add New Chart:
→ Modify: `visualizer.py`

### To Change Pipeline Flow:
→ Modify: `main.py`

### To Customize LLM Analysis:
→ Modify: `llm_prompts.py`

---

This architecture ensures **modularity**, **flexibility**, and **extensibility**!
