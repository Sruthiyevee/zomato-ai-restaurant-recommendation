"""
Storage Module for Phase 1
Handles data persistence and storage operations
"""

import logging
import pandas as pd
import sqlite3
import json
from typing import Dict, List, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZomatoDataStorage:
    """Manages storage of processed Zomato restaurant data"""
    
    def __init__(self, db_path: str = "phase_1_data_ingestion/data/processed/zomato_restaurants.db"):
        """
        Initialize the storage manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._ensure_db_directory()
        
    def _ensure_db_directory(self) -> None:
        """Ensure database directory exists"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def create_schema(self) -> None:
        """Create database schema"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Restaurant master table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                restaurant_id INTEGER PRIMARY KEY,
                restaurant_name TEXT NOT NULL,
                city TEXT NOT NULL,
                primary_cuisine TEXT,
                price_range TEXT,
                normalized_rating REAL,
                review_count INTEGER,
                latitude REAL,
                longitude REAL,
                popularity_score REAL,
                composite_score REAL,
                recency_score REAL,
                cuisine_list TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for efficient querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_city ON restaurants(city)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_range ON restaurants(price_range)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_composite_score ON restaurants(composite_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_city_price ON restaurants(city, price_range)")
        
        # Review aggregation table (if needed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_aggregations (
                restaurant_id INTEGER PRIMARY KEY,
                average_rating REAL,
                total_reviews INTEGER,
                sentiment_score REAL,
                last_review_date TEXT,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
            )
        """)
        
        self.conn.commit()
        logger.info("Database schema created successfully")
    
    def store_data(self, data: pd.DataFrame) -> None:
        """
        Store processed data in database
        
        Args:
            data: Processed pandas DataFrame
        """
        if not self.conn:
            self.connect()
        
        if data is None or data.empty:
            raise ValueError("No data to store")
        
        # Ensure schema exists
        self.create_schema()
        
        # Prepare data for insertion
        # Select required columns
        required_columns = [
            'restaurant_id', 'restaurant_name', 'city', 'primary_cuisine',
            'price_range', 'normalized_rating', 'review_count',
            'latitude', 'longitude', 'popularity_score', 'composite_score',
            'recency_score', 'cuisine_list'
        ]
        
        # Check which columns exist
        available_columns = [col for col in required_columns if col in data.columns]
        
        # Create subset with available columns
        store_data = data[available_columns].copy()
        
        # Convert cuisine_list to string if it's a list
        if 'cuisine_list' in store_data.columns:
            store_data['cuisine_list'] = store_data['cuisine_list'].apply(
                lambda x: json.dumps(x) if isinstance(x, list) else str(x)
            )
        
        # Replace NaN with None for SQL
        store_data = store_data.where(pd.notna(store_data), None)
        
        # Clear existing data (optional - can be made configurable)
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM restaurants")
        
        # Insert data
        placeholders = ', '.join(['?' for _ in available_columns])
        columns_str = ', '.join(available_columns)
        
        insert_query = f"INSERT INTO restaurants ({columns_str}) VALUES ({placeholders})"
        
        records = store_data.to_dict('records')
        cursor.executemany(insert_query, [tuple(record.values()) for record in records])
        
        self.conn.commit()
        logger.info(f"Stored {len(records)} restaurant records in database")
    
    def save_to_csv(self, data: pd.DataFrame, filepath: str) -> None:
        """
        Save data to CSV file
        
        Args:
            data: pandas DataFrame to save
            filepath: Path to save CSV file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data.to_csv(filepath, index=False)
        logger.info(f"Data saved to CSV: {filepath}")
    
    def save_to_json(self, data: pd.DataFrame, filepath: str) -> None:
        """
        Save data to JSON file
        
        Args:
            data: pandas DataFrame to save
            filepath: Path to save JSON file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to records format
        records = data.to_dict('records')
        
        # Handle list columns for JSON serialization
        for record in records:
            for key, value in record.items():
                if isinstance(value, (list, tuple)):
                    record[key] = list(value)
                elif pd.isna(value):
                    record[key] = None
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Data saved to JSON: {filepath}")
    
    def load_from_db(self, query: str = "SELECT * FROM restaurants") -> pd.DataFrame:
        """
        Load data from database
        
        Args:
            query: SQL query to execute
            
        Returns:
            pandas DataFrame with query results
        """
        if not self.conn:
            self.connect()
        
        df = pd.read_sql_query(query, self.conn)
        
        # Parse JSON columns
        if 'cuisine_list' in df.columns:
            df['cuisine_list'] = df['cuisine_list'].apply(
                lambda x: json.loads(x) if x and isinstance(x, str) else []
            )
        
        return df
    
    def get_storage_stats(self) -> Dict:
        """Get statistics about stored data"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM restaurants")
        total_count = cursor.fetchone()[0]
        
        # Get city distribution
        cursor.execute("SELECT city, COUNT(*) FROM restaurants GROUP BY city")
        city_dist = dict(cursor.fetchall())
        
        # Get price range distribution
        cursor.execute("SELECT price_range, COUNT(*) FROM restaurants GROUP BY price_range")
        price_dist = dict(cursor.fetchall())
        
        # Get average rating
        cursor.execute("SELECT AVG(normalized_rating) FROM restaurants")
        avg_rating = cursor.fetchone()[0] or 0
        
        return {
            'total_restaurants': total_count,
            'cities': len(city_dist),
            'city_distribution': city_dist,
            'price_range_distribution': price_dist,
            'average_rating': round(avg_rating, 2)
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
