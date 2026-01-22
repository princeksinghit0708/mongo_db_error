# Supported Collection Structures

This system supports multiple MongoDB collection structures and automatically normalizes them for analysis.

## Collection Type 1: Simple Structure (e.g., "abc")

**Fields:**
- `errorType`: Error type identifier
- `rawData`: Raw input data
- `type`: Data type/category
- `timestamp`: Error timestamp
- `uuid`: Unique identifier

**Example:**
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

## Collection Type 2: Nested Event Structure (e.g., "cde")

**Fields:**
- `event.header.*`: Error and metadata information
  - `errorCode`: Error code
  - `errorDetails`: Detailed error message
  - `timestamp`: Event timestamp
  - `businessCode`, `domain`, `channel`, `countryCode`: Business metadata
- `event.body.*`: Transaction/data details
  - `accountNumber`, `transactionAmount`, `merchantIdentifier`: Transaction data
- `dataSavedAtTimeStamp`: Record save timestamp

**Example:**
```json
{
  "_id": ObjectId("..."),
  "event": {
    "header": {
      "name": "IBSCardAuthorization",
      "version": "1.0",
      "errorCode": "ENRICH_ERR_CCID_FRM_CLTIDLAST4CARDNUM",
      "errorDetails": "Event enrichment failed...",
      "timestamp": "2025-11-05T16:30:02Z",
      "businessCode": "CARDS",
      "domain": "Payments",
      "channel": "IBSCardAuthorization",
      "countryCode": "US"
    },
    "body": {
      "accountNumber": "5424181148038180",
      "merchantIdentifier": "000526200367880",
      "merchantCategoryCode": "6051",
      "transactionAmount": "220.0"
    }
  },
  "dataSavedAtTimeStamp": "2025-11-05T16:30:03.432+00:00"
}
```

## Automatic Normalization

The system automatically:

1. **Flattens nested structures**: 
   - `event.header.errorCode` → `header_errorCode`
   - `event.body.transactionAmount` → `body_transactionAmount`

2. **Maps error fields**:
   - `errorCode` → `errorType` (for consistency)

3. **Handles timestamps**:
   - Uses `dataSavedAtTimeStamp`, `eventTransactionTime`, or `timestamp` as available

4. **Extracts features**:
   - From both simple and nested structures
   - Creates ML-ready features from all available fields

## Usage

Simply specify the collection names when running the analysis:

```python
COLLECTIONS_TO_ANALYZE = ['abc', 'cde']  # Both collection types
```

The system will automatically detect and normalize the different structures.
