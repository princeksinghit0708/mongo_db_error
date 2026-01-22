# Quick Start Guide

## Step 1: Install Dependencies

```bash
cd "Mongodb_error_predictive analysis"
pip install -r requirements.txt
```

## Step 2: Configure MongoDB Connection

Edit `example_usage.py` or `main.py` and update:

```python
MONGODB_CONNECTION_STRING = 'mongodb://your_host:27017/'  # Your MongoDB URI
DATABASE_NAME = 'your_database_name'  # Your database name
```

## Step 3: Run Analysis

### Option A: Using the example script (recommended for first run)

```bash
python example_usage.py
```

### Option B: Using the main script

```bash
python main.py
```

## Step 4: View Results

After running, check the `output/` directory for:
- **Visualizations**: PNG charts showing error patterns
- **Reports**: JSON and TXT files with detailed analysis

## Example: Analyzing Collection 'abc'

To specifically analyze your 'abc' collection:

1. Open `example_usage.py`
2. Set `COLLECTIONS_TO_ANALYZE = ['abc']`
3. Update MongoDB connection details
4. Run: `python example_usage.py`

## Optional: Enable LLM Analysis

For intelligent error reason analysis using Google Gemini:

1. Get a Gemini API key from https://makersuite.google.com/app/apikey
2. Set it in your environment:
   ```bash
   export GEMINI_API_KEY='your-key-here'
   ```
   Or add it directly in the script:
   ```python
   GEMINI_API_KEY = 'your-key-here'
   ```

## What You'll Get

1. **Error Frequency Analysis**: Which errors occur most often
2. **Temporal Patterns**: When errors occur (daily/hourly trends)
3. **Predictive Models**: ML models that can predict error types
4. **Future Predictions**: Expected error counts for next 7 days
5. **LLM Insights**: AI-powered explanations of why errors occur
6. **Visualizations**: Charts and dashboards
7. **Recommendations**: Actionable insights to reduce errors

## Troubleshooting

- **Connection Error**: Verify MongoDB is running and connection string is correct
- **No Data Found**: Check collection names match your database
- **Import Errors**: Run `pip install -r requirements.txt` again
