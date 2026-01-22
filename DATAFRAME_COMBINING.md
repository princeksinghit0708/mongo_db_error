# How DataFrames Are Combined

## 🔄 Combining Process

### Step 1: Adding Source Identifier
**Location**: `mongodb_connector.py` → `read_multiple_collections()` (line 207)

```python
for collection_name in collection_names:
    df = self.read_collection(collection_name, query, limit)
    if not df.empty:
        # Add collection name as a column for tracking
        df['source_collection'] = collection_name  # ← COMMON FIELD ADDED
        data_dict[collection_name] = df
```

**What happens**: Each DataFrame gets a `source_collection` column added to track its origin.

### Step 2: Concatenation
**Location**: `error_analyzer.py` → `_combine_data()` (line 43)

```python
def _combine_data(self):
    dfs = []
    for collection_name, df in self.data_dict.items():
        if not df.empty:
            dfs.append(df)
    
    if dfs:
        self.combined_df = pd.concat(dfs, ignore_index=True)
```

**What happens**: All DataFrames are stacked vertically using `pd.concat()`.

## 🔑 Common Fields (What Makes Combination Possible)

### 1. **`source_collection`** (Always Present)
- **Purpose**: Tracks which collection each row came from
- **Added by**: `mongodb_connector.py`
- **Example values**: `'abc'`, `'cde'`, `'errors'`
- **Why important**: Allows analysis by collection

### 2. **Error Fields** (Normalized to Common Names)
- **`errorType`** or **`errorCode`** → Both mapped to `errorType`
- **Normalization**: `mongodb_connector.py` maps `errorCode` → `errorType`
- **Why important**: Unified error analysis across collections

### 3. **Timestamp Fields** (Normalized)
- **Possible fields**: `timestamp`, `dataSavedAtTimeStamp`, `eventTransactionTime`
- **Normalization**: All mapped to `timestamp` column
- **Why important**: Temporal analysis works across collections

### 4. **Common MongoDB Fields**
- **`_id`**: Document ID (always present)
- **`uuid`**: Unique identifier (if present)

## 📊 Example: Combining Two Collections

### Collection "abc" DataFrame:
```
| _id | rawData | errorType | type | timestamp | uuid |
|-----|---------|-----------|------|-----------|------|
| 1   | 12345   | ERR_001   | BIN  | 2024-01-01| uuid1|
| 2   | 67890   | ERR_002   | BIN  | 2024-01-02| uuid2|
```

### Collection "cde" DataFrame:
```
| _id | header_errorCode | header_domain | body_transactionAmount | dataSavedAtTimeStamp |
|-----|------------------|---------------|------------------------|---------------------|
| 3   | ERR_003          | Payments      | 220.0                  | 2024-01-03         |
| 4   | ERR_004          | Payments      | 150.0                  | 2024-01-04         |
```

### After Normalization (in mongodb_connector):
**Collection "abc"**:
```
| _id | rawData | errorType | type | timestamp | uuid | source_collection |
|-----|---------|-----------|------|-----------|------|------------------|
| 1   | 12345   | ERR_001   | BIN  | 2024-01-01| uuid1| abc              |
| 2   | 67890   | ERR_002   | BIN  | 2024-01-02| uuid2| abc              |
```

**Collection "cde"**:
```
| _id | errorType | header_domain | body_transactionAmount | timestamp | source_collection |
|-----|-----------|---------------|------------------------|-----------|------------------|
| 3   | ERR_003   | Payments      | 220.0                  | 2024-01-03| cde              |
| 4   | ERR_004   | Payments      | 150.0                  | 2024-01-04| cde              |
```
*Note: `errorCode` → `errorType`, `dataSavedAtTimeStamp` → `timestamp`*

### After Concatenation (Combined DataFrame):
```
| _id | rawData | errorType | type | timestamp | uuid | source_collection | header_domain | body_transactionAmount |
|-----|---------|-----------|------|-----------|------|------------------|---------------|------------------------|
| 1   | 12345   | ERR_001   | BIN  | 2024-01-01| uuid1| abc              | NaN           | NaN                    |
| 2   | 67890   | ERR_002   | BIN  | 2024-01-02| uuid2| abc              | NaN           | NaN                    |
| 3   | NaN     | ERR_003   | NaN  | 2024-01-03| NaN  | cde              | Payments      | 220.0                  |
| 4   | NaN     | ERR_004   | NaN  | 2024-01-04| NaN  | cde              | Payments      | 150.0                  |
```

## 🎯 Key Points

### 1. **Pandas `concat()` Behavior**
- **Combines by columns**: If columns match, they align
- **Missing columns**: Filled with `NaN` for rows that don't have that column
- **`ignore_index=True`**: Resets index to 0, 1, 2, 3...

### 2. **Common Fields That Enable Analysis**
- **`source_collection`**: Always present, tracks origin
- **`errorType`**: Normalized from `errorCode` if needed
- **`timestamp`**: Normalized from various timestamp fields
- **`_id`**: Always present (MongoDB document ID)

### 3. **Collection-Specific Fields**
- **"abc" collection**: `rawData`, `type`, `uuid`
- **"cde" collection**: `header_domain`, `body_transactionAmount`, etc.
- **Analysis handles**: Missing fields are `NaN`, which pandas handles gracefully

## 🔍 How It's Used in Analysis

### Example 1: Error Frequency by Collection
```python
# Uses source_collection + errorType
freq_df = combined_df.groupby(['source_collection', 'errorType']).size()
```

### Example 2: Temporal Analysis
```python
# Uses timestamp (normalized from various sources)
df['date'] = df['timestamp'].dt.date
temporal_df = df.groupby(['date', 'errorType']).size()
```

### Example 3: Collection-Specific Analysis
```python
# Can filter by source_collection
abc_errors = combined_df[combined_df['source_collection'] == 'abc']
cde_errors = combined_df[combined_df['source_collection'] == 'cde']
```

## 📝 Summary

**Common Things for Combining:**
1. ✅ **`source_collection`** - Added to every DataFrame
2. ✅ **`errorType`** - Normalized from `errorCode` if needed
3. ✅ **`timestamp`** - Normalized from various timestamp fields
4. ✅ **`_id`** - Always present from MongoDB

**How Combination Works:**
- `pd.concat()` stacks DataFrames vertically
- Missing columns become `NaN`
- All rows keep their `source_collection` identifier
- Analysis can filter by collection or analyze all together

**Result:**
- Single unified DataFrame with all error data
- Can analyze across collections or per collection
- Handles different collection structures gracefully
