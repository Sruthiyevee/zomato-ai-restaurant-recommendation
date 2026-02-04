# Phase 1: Data Ingestion

This phase handles the complete data ingestion pipeline for the Zomato AI Restaurant Recommendation Service.

## Overview

Phase 1 implements the following components:
1. **Data Loader**: Ingests Zomato dataset from Hugging Face
2. **Data Cleaner**: Performs comprehensive data cleaning
3. **Data Preprocessor**: Engineers features and preprocesses data
4. **Storage Manager**: Stores processed data in SQLite database

## Folder Structure

```
phase_1_data_ingestion/
├── src/
│   ├── __init__.py
│   ├── loader.py          # Dataset loading from Hugging Face
│   ├── cleaner.py         # Data cleaning operations
│   ├── preprocessor.py    # Feature engineering and preprocessing
│   ├── storage.py         # Database storage operations
│   └── pipeline.py         # Complete pipeline orchestration
├── tests/
│   ├── test_loader.py     # Tests for data loader
│   ├── test_cleaner.py    # Tests for data cleaner
│   ├── test_preprocessor.py  # Tests for preprocessor
│   ├── test_storage.py    # Tests for storage manager
│   └── test_pipeline.py   # Integration tests
├── data/
│   ├── raw/               # Raw dataset files
│   └── processed/         # Processed data files and database
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Complete Pipeline

```python
from src.pipeline import Phase1Pipeline

pipeline = Phase1Pipeline()
processed_data = pipeline.run()
```

### Individual Components

#### Load Data
```python
from src.loader import ZomatoDataLoader

loader = ZomatoDataLoader()
raw_data = loader.load_dataset()
```

#### Clean Data
```python
from src.cleaner import ZomatoDataCleaner

cleaner = ZomatoDataCleaner(raw_data)
cleaned_data = cleaner.clean()
```

#### Preprocess Data
```python
from src.preprocessor import ZomatoDataPreprocessor

preprocessor = ZomatoDataPreprocessor(cleaned_data)
processed_data = preprocessor.preprocess()
```

#### Store Data
```python
from src.storage import ZomatoDataStorage

storage = ZomatoDataStorage()
storage.connect()
storage.create_schema()
storage.store_data(processed_data)
```

## Running Tests

Run all tests:
```bash
python -m pytest tests/
```

Run specific test file:
```bash
python -m pytest tests/test_loader.py
```

Run with verbose output:
```bash
python -m pytest tests/ -v
```

## Data Cleaning Operations

The cleaner performs the following operations:
- Missing value handling (critical fields, ratings, prices)
- Duplicate removal
- Text field normalization
- Data type validation and conversion
- Outlier detection and handling
- Text data cleaning (HTML removal, special characters)
- Categorical field standardization

## Preprocessing Operations

The preprocessor performs:
- Feature engineering (restaurant IDs, names, cities)
- Price range categorization (Budget, Mid-Range, Premium, Luxury)
- Rating normalization (0-5 scale)
- Review aggregation and recency scoring
- Popularity metric calculation
- Cuisine encoding (lists, primary cuisine)
- Geospatial processing (latitude/longitude validation)
- Composite score creation for ranking

## Storage

Data is stored in SQLite database with the following schema:
- **restaurants** table: Main restaurant data with indexes on city, price_range, and composite_score
- **review_aggregations** table: Aggregated review metrics

Processed data is also saved as:
- CSV file: `data/processed/zomato_processed_data.csv`
- JSON file: `data/processed/zomato_processed_data.json`
- SQLite database: `data/processed/zomato_restaurants.db`

## Output

After running the pipeline, you will have:
1. Cleaned and preprocessed restaurant data
2. SQLite database with indexed restaurant records
3. CSV and JSON exports of processed data
4. Statistics and summaries of the processing steps

## Next Steps

After Phase 1 completion, the processed data is ready for:
- Phase 2: User input collection and validation
- Phase 3: Integration layer for filtering and business logic
- Phase 4: Recommendation engine with Groq LLM
- Phase 5: Result display and formatting
