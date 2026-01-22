# MongoDB Error Predictive Analytics

A comprehensive solution for analyzing MongoDB error patterns and running predictive analytics to understand error reasons, frequency, and future occurrences.

## Features

- **Multi-Collection Analysis**: Read and analyze errors from multiple MongoDB collections
- **Error Pattern Analysis**: Identify error types, frequencies, and temporal patterns
- **Predictive Analytics**: Use Machine Learning (Random Forest, Gradient Boosting, XGBoost) to predict error patterns
- **LLM Integration**: Leverage Google Gemini 3.0 for intelligent error reason analysis
- **Visualization**: Generate comprehensive charts and dashboards
- **Automated Reporting**: Create detailed analysis reports with recommendations

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional, create a `.env` file):
```bash
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=your_database_name
GEMINI_API_KEY=your_gemini_api_key_here  # Optional, for LLM analysis
```

## Usage

### Basic Usage

1. **Update connection details in `main.py`**:
   - Set `MONGODB_CONNECTION_STRING` to your MongoDB connection string
   - Set `DATABASE_NAME` to your database name
   - Optionally set `GEMINI_API_KEY` for LLM analysis

2. **Run the analysis**:
```bash
python main.py
```

### Configuration Options

In `main.py`, you can customize:

- **`COLLECTIONS_TO_ANALYZE`**: Specify specific collections (e.g., `['abc', 'errors']`) or `None` for auto-detection
- **`DOCUMENT_LIMIT`**: Limit number of documents per collection (e.g., `10000`) or `None` for all documents
- **`GEMINI_API_KEY`**: Your Google Gemini API key for LLM-powered error analysis

### Programmatic Usage

```python
from main import ErrorAnalysisPipeline

pipeline = ErrorAnalysisPipeline(
    connection_string="mongodb://localhost:27017/",
    database_name="your_database",
    gemini_api_key="your_key"  # Optional
)

pipeline.run_full_analysis(
    collection_names=['abc', 'errors'],  # Optional
    limit=10000  # Optional
)
```

## Output

The analysis generates:

1. **Visualizations** (in `output/` directory):
   - `error_frequency.png`: Error type frequency chart
   - `temporal_trends.png`: Daily and hourly error trends
   - `collection_distribution.png`: Error distribution across collections
   - `model_performance.png`: ML model accuracy comparison
   - `feature_importance.png`: Feature importance from ML models
   - `summary_dashboard.png`: Comprehensive dashboard

2. **Reports**:
   - `analysis_report.json`: Detailed JSON report
   - `analysis_report.txt`: Human-readable text report

## Data Structure

The system supports multiple MongoDB collection structures. It automatically normalizes different formats:

### Collection Type 1: Simple Error Structure (e.g., "abc" collection)

- `errorType`: Type of error (e.g., "INCORRECT_INPUT_LENGTH")
- `timestamp`: Timestamp of the error
- `rawData`: Raw data that caused the error
- `type`: Type/category (e.g., "BIN")
- `uuid`: Unique identifier
- `_id`: MongoDB document ID

Example:
```json
{
  "_id": ObjectId("66e7d8e1c26f1109665298e9"),
  "rawData": "779999046767",
  "uuid": "ac8db6fc-8b42-4db6-b720-9dff898e84cf",
  "timestamp": "2024-09-16T07:06:09.392+00:00",
  "errorType": "INCORRECT_INPUT_LENGTH",
  "type": "BIN"
}
```

### Collection Type 2: Nested Event Structure (e.g., "cde" collection)

- `event.header`: Contains error information and metadata
  - `errorCode`: Error code (e.g., "ENRICH_ERR_CCID_FRM_CLTIDLAST4CARDNUM")
  - `errorDetails`: Detailed error message
  - `timestamp`: Event timestamp
  - `businessCode`, `domain`, `channel`, `countryCode`: Business metadata
- `event.body`: Contains transaction/data details
  - `accountNumber`, `transactionAmount`, `merchantIdentifier`: Transaction data
- `dataSavedAtTimeStamp`: When the record was saved
- `_id`: MongoDB document ID

Example:
```json
{
  "_id": ObjectId("..."),
  "event": {
    "header": {
      "errorCode": "ENRICH_ERR_CCID_FRM_CLTIDLAST4CARDNUM",
      "errorDetails": "Event enrichment failed...",
      "timestamp": "2025-11-05T16:30:02Z",
      "businessCode": "CARDS",
      "domain": "Payments"
    },
    "body": {
      "accountNumber": "5424181148038180",
      "transactionAmount": "220.0"
    }
  },
  "dataSavedAtTimeStamp": "2025-11-05T16:30:03.432+00:00"
}
```

The system automatically:
- Flattens nested structures (`event.header.*` → `header_*`)
- Maps `errorCode` to `errorType` for consistency
- Handles different timestamp field names
- Extracts features from both collection types

## Modules

- **`mongodb_connector.py`**: Handles MongoDB connections and data extraction
- **`error_analyzer.py`**: Analyzes error patterns and frequencies
- **`predictive_analytics.py`**: ML models and LLM integration for predictions
- **`llm_prompts.py`**: LLM prompt templates for error analysis (customizable)
- **`visualizer.py`**: Creates charts and visualizations
- **`main.py`**: Main pipeline orchestrator

## Machine Learning Models

The system trains three ML models:

1. **Random Forest**: Ensemble method using multiple decision trees
2. **Gradient Boosting**: Sequential ensemble method
3. **XGBoost**: Optimized gradient boosting implementation

All models predict error types based on features extracted from:
- Temporal patterns (hour, day, month)
- Raw data characteristics (length, type)
- Collection source
- Other available fields

## LLM Analysis

When Google Gemini API key is provided, the system uses Gemini 3.0 models to:
- Analyze error reasons
- Explain why errors occur
- Identify root causes
- Provide recommendations

**Customizable Prompts**: The LLM prompts are stored in `llm_prompts.py` and can be easily customized to:
- Change the analysis focus
- Add specific requirements
- Modify the output format
- Include additional context

Get your Gemini API key from: https://makersuite.google.com/app/apikey

## Requirements

- Python 3.8+
- MongoDB database with error collections
- (Optional) Google Gemini API key for LLM analysis

## Troubleshooting

1. **Connection Issues**: Verify MongoDB connection string and database name
2. **No Data Found**: Check collection names and ensure they contain error data
3. **LLM Errors**: Verify Gemini API key and ensure you have API access
4. **Import Errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## License

This project is provided as-is for error analysis and predictive analytics purposes.
