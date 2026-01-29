# Pipeline Using SQLite as Data Source

## Overview

The pipeline now uses **SQLite as the analysis data source** when `use_sqlite=True`:

1. **data_source='mongodb'**: Read from MongoDB → store in SQLite → **load from SQLite** → run analysis (ErrorAnalyzer, PredictiveAnalytics, etc.).
2. **data_source='sqlite'**: **Load only from SQLite** → run analysis (no MongoDB connection).

So analysis (patterns, ML, LLM, visualizations) always runs on data that was loaded from SQLite when `use_sqlite=True`, ensuring a single source of truth in SQLite.

## Flow

```
data_source='mongodb':
  MongoDB → connector (schema extraction) → data_dict
       → store_errors(combined_df) → SQLite
       → load_all_errors() → combined_df
       → _dataframe_to_data_dict() → data_dict
       → ErrorAnalyzer(data_dict) → ... rest of pipeline

data_source='sqlite':
  load_all_errors() → combined_df
       → _dataframe_to_data_dict() → data_dict
       → ErrorAnalyzer(data_dict) → ... rest of pipeline
```

## Usage

### First run: populate SQLite from MongoDB

```python
pipeline = ErrorAnalysisPipeline(
    connection_string="mongodb://...",
    database_name="my_db",
    use_sqlite=True,
    data_source="mongodb"
)
pipeline.run_full_analysis(collection_names=['abc', 'cde'])
# Data is stored in error_analytics.db; analysis uses data from SQLite
```

### Later runs: analyze from SQLite only (no MongoDB)

```python
pipeline = ErrorAnalysisPipeline(
    connection_string="mongodb://...",  # not used
    database_name="my_db",
    use_sqlite=True,
    data_source="sqlite"
)
pipeline.run_full_analysis()  # collection_names/limit ignored
# Loads from error_analytics.db only
```

### Environment variable

```bash
export DATA_SOURCE=sqlite   # load only from SQLite
python example_usage.py
```

## Files changed

- **main.py**: `data_source` param; MongoDB → store → load from SQLite → `_dataframe_to_data_dict` → ErrorAnalyzer; `data_source='sqlite'` path; cleanup only if connector exists.
- **sqlite_store.py**: `load_all_errors()`; `get_table_columns()`; `store_errors()` filters columns to table schema; indexes created separately; `errorMessage`, `uuid` in table.
- **example_usage.py** / **example_with_storage.py**: `data_source` and `use_sqlite=True` in pipeline constructor.

## SQLite table

- Table `errors`: columns aligned with pipeline/schema (e.g. `source_collection`, `errorType`, `timestamp`, `rawData`, `type`, `domain`, `businessCode`, `transactionAmount`, `merchantIdentifier`, `errorDetails`, `errorMessage`, `uuid`).
- `store_errors()` only writes columns that exist in the table.
- `load_all_errors()` returns all rows (excluding `id`, `created_at`) and parses `timestamp` to datetime.

## Backward compatibility

- `use_sqlite=False`: pipeline uses in-memory data from MongoDB only (no SQLite).
- `data_source` defaults to `'mongodb'`.
- Existing `error_analyzer.py`, `predictive_analytics.py`, `visualizer.py` unchanged; they still receive `data_dict` and `combined_df` from main.
