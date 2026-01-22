# Complete System Flow Structure

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRY POINT                                   │
│  example_usage.py or main.py                                     │
│  - Configures MongoDB connection                                 │
│  - Sets up Gemini API key (optional)                             │
│  - Specifies collections to analyze                             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              ErrorAnalysisPipeline                               │
│              (main.py - ErrorAnalysisPipeline class)              │
│                                                                   │
│  Orchestrates the entire 7-step pipeline                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
```

## 📊 Complete Flow Diagram

### STEP 1: MongoDB Connection
```
┌─────────────────────────────────────┐
│  MongoDBConnector                   │
│  (mongodb_connector.py)             │
│                                     │
│  • connect()                        │
│    - Establishes MongoDB connection │
│    - Tests connection with ping      │
│    - Returns True/False             │
└──────────────┬──────────────────────┘
               │
               ▼
```

### STEP 2: Data Extraction
```
┌─────────────────────────────────────┐
│  read_multiple_collections()        │
│  or get_error_collections()         │
│                                     │
│  For each collection:              │
│  1. read_collection()               │
│     - Queries MongoDB               │
│     - Converts to pandas DataFrame  │
│     - Normalizes nested structures   │
│       (event.header → header_*)      │
│     - Maps errorCode → errorType    │
│     - Handles timestamps            │
│                                     │
│  Returns:                           │
│  data_dict = {                      │
│    'abc': DataFrame,                 │
│    'cde': DataFrame,                │
│    ...                              │
│  }                                  │
└──────────────┬──────────────────────┘
               │
               ▼
```

### STEP 3: Error Pattern Analysis
```
┌─────────────────────────────────────┐
│  ErrorAnalyzer                       │
│  (error_analyzer.py)                 │
│                                     │
│  __init__(data_dict):               │
│    • Receives data_dict             │
│    • Combines all DataFrames        │
│      into self.combined_df          │
│                                     │
│  get_error_patterns():              │
│    • Error type frequency           │
│    • Collection distribution        │
│    • Temporal patterns (daily/hourly)│
│    • Raw data length stats          │
│    • Transaction amount stats       │
│                                     │
│  get_summary_statistics():          │
│    • Total records                  │
│    • Unique error types             │
│    • Date ranges                    │
└──────────────┬──────────────────────┘
               │
               ▼
```

### STEP 4: Predictive Analytics
```
┌─────────────────────────────────────┐
│  PredictiveAnalytics                 │
│  (predictive_analytics.py)          │
│                                     │
│  A. Feature Engineering:            │
│     prepare_features():              │
│       • Temporal: hour, day, month  │
│       • Raw data: length, type       │
│       • Transaction: amount, log     │
│       • Categorical encoding         │
│                                     │
│  B. ML Model Training:              │
│     train_error_prediction_model():  │
│       • Random Forest               │
│       • Gradient Boosting           │
│       • XGBoost                     │
│       • Returns accuracy & metrics  │
│                                     │
│  C. Frequency Analysis:             │
│     analyze_error_frequency_patterns()│
│       • Daily trends                │
│       • Most frequent errors        │
│                                     │
│  D. Future Predictions:              │
│     predict_future_errors():        │
│       • 7-day ahead predictions     │
│       • Based on historical patterns│
│                                     │
│  E. Feature Importance:              │
│     get_feature_importance():       │
│       • Which features matter most  │
└──────────────┬──────────────────────┘
               │
               ▼
```

### STEP 5: LLM Analysis (Optional)
```
┌─────────────────────────────────────┐
│  Gemini LLM Integration              │
│  (predictive_analytics.py)          │
│                                     │
│  predict_error_reason_llm():        │
│    1. Gets prompt from              │
│       llm_prompts.py                │
│    2. Formats error record          │
│    3. Calls Gemini API              │
│    4. Returns analysis:             │
│       • Error reason                │
│       • Root causes                 │
│       • Recommendations            │
│                                     │
│  Analyzes sample of each            │
│  error type (max 3 for cost)        │
└──────────────┬──────────────────────┘
               │
               ▼
```

### STEP 6: Visualization
```
┌─────────────────────────────────────┐
│  ErrorVisualizer                     │
│  (visualizer.py)                    │
│                                     │
│  Generates charts:                  │
│    • error_frequency.png            │
│    • temporal_trends.png            │
│    • collection_distribution.png    │
│    • model_performance.png           │
│    • feature_importance.png         │
│    • summary_dashboard.png          │
│                                     │
│  All saved to output/ directory     │
└──────────────┬──────────────────────┘
               │
               ▼
```

### STEP 7: Report Generation
```
┌─────────────────────────────────────┐
│  Report Generation                   │
│  (main.py - _generate_report())     │
│                                     │
│  Creates:                           │
│    • analysis_report.json           │
│      - Summary statistics           │
│      - Error patterns               │
│      - Model performance            │
│      - Future predictions           │
│      - LLM analysis                 │
│      - Recommendations             │
│                                     │
│    • analysis_report.txt            │
│      - Human-readable format        │
│                                     │
│  Saved to output/ directory         │
└─────────────────────────────────────┘
```

## 🔄 Complete Data Flow

```
MongoDB Database
    │
    │ (pymongo queries)
    ▼
mongodb_connector.py
    │
    │ Returns: data_dict = {'collection_name': DataFrame}
    ▼
error_analyzer.py
    │
    │ Combines → combined_df (pandas DataFrame)
    │ Analyzes patterns
    ▼
predictive_analytics.py
    │
    │ Feature Engineering
    │ ML Model Training
    │ Future Predictions
    │
    ├──► LLM Analysis (Gemini API)
    │
    ▼
visualizer.py
    │
    │ Generates PNG charts
    ▼
main.py (_generate_report)
    │
    │ Creates JSON & TXT reports
    ▼
output/ directory
    │
    ├── error_frequency.png
    ├── temporal_trends.png
    ├── collection_distribution.png
    ├── model_performance.png
    ├── feature_importance.png
    ├── summary_dashboard.png
    ├── analysis_report.json
    └── analysis_report.txt
```

## 📁 Module Responsibilities

### 1. **mongodb_connector.py**
   - **Purpose**: MongoDB data extraction
   - **Key Functions**:
     - `connect()`: Establishes MongoDB connection
     - `read_collection()`: Reads single collection
     - `read_multiple_collections()`: Reads multiple collections
     - `_normalize_nested_structure()`: Flattens nested MongoDB documents
   - **Output**: Dictionary of pandas DataFrames

### 2. **error_analyzer.py**
   - **Purpose**: Pattern analysis and statistics
   - **Key Functions**:
     - `get_error_type_frequency()`: Counts error occurrences
     - `get_temporal_analysis()`: Time-based patterns
     - `get_error_patterns()`: Comprehensive pattern analysis
   - **Output**: Analysis dictionaries and DataFrames

### 3. **predictive_analytics.py**
   - **Purpose**: ML predictions and LLM analysis
   - **Key Functions**:
     - `prepare_features()`: Feature engineering
     - `train_error_prediction_model()`: Trains 3 ML models
     - `predict_future_errors()`: 7-day predictions
     - `predict_error_reason_llm()`: Gemini LLM analysis
   - **Output**: Model results, predictions, LLM insights

### 4. **visualizer.py**
   - **Purpose**: Chart generation
   - **Key Functions**:
     - `plot_error_frequency()`: Bar charts
     - `plot_temporal_trends()`: Time series
     - `create_summary_dashboard()`: Combined dashboard
   - **Output**: PNG image files

### 5. **llm_prompts.py**
   - **Purpose**: LLM prompt templates
   - **Key Functions**:
     - `get_error_analysis_prompt()`: Main error analysis prompt
   - **Output**: Formatted prompt strings

### 6. **main.py**
   - **Purpose**: Pipeline orchestration
   - **Key Class**: `ErrorAnalysisPipeline`
   - **Orchestrates**: All 7 steps sequentially
   - **Output**: Complete analysis results

## 🎯 Execution Flow Example

```python
# 1. User runs example_usage.py
pipeline = ErrorAnalysisPipeline(
    connection_string="mongodb://...",
    database_name="my_db",
    gemini_api_key="..."
)

# 2. Pipeline executes 7 steps:
pipeline.run_full_analysis(
    collection_names=['abc', 'cde'],
    limit=None
)

# Internal execution:
# Step 1: connector.connect() → MongoDB connection
# Step 2: connector.read_multiple_collections() → Data extraction
# Step 3: ErrorAnalyzer(data_dict) → Pattern analysis
# Step 4: PredictiveAnalytics(df) → ML & predictions
# Step 5: predictor.predict_error_reason_llm() → LLM analysis
# Step 6: visualizer.plot_*() → Generate charts
# Step 7: _generate_report() → Create reports
```

## 🔑 Key Design Patterns

1. **Separation of Concerns**: Each module has a single responsibility
2. **Data Pipeline**: Sequential processing with clear data flow
3. **Error Handling**: Try-except blocks at critical points
4. **Flexibility**: Supports multiple collection structures
5. **Modularity**: Easy to extend or modify individual components

## 📊 Data Transformations

```
MongoDB Documents (BSON)
    ↓
Pandas DataFrames
    ↓
Normalized DataFrames (flattened structures)
    ↓
Feature Engineered DataFrames (ML-ready)
    ↓
ML Model Predictions
    ↓
Visualizations & Reports
```

This architecture ensures:
- ✅ Clean separation of data, analysis, and presentation
- ✅ Easy to test individual components
- ✅ Scalable to handle more collections
- ✅ Extensible for new analysis types
