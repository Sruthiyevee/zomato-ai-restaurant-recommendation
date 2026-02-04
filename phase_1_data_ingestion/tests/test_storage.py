"""
Test cases for Storage Module
"""

import unittest
import pandas as pd
import sqlite3
import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from storage import ZomatoDataStorage


class TestZomatoDataStorage(unittest.TestCase):
    """Test cases for ZomatoDataStorage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_db_path = "phase_1_data_ingestion/data/processed/test_zomato.db"
        self.storage = ZomatoDataStorage(db_path=self.test_db_path)
        
        # Create sample processed data
        self.sample_data = pd.DataFrame({
            'restaurant_id': [1, 2, 3],
            'restaurant_name': ['Restaurant A', 'Restaurant B', 'Restaurant C'],
            'city': ['Mumbai', 'Delhi', 'Bangalore'],
            'primary_cuisine': ['Italian', 'Chinese', 'Indian'],
            'price_range': ['Mid-Range', 'Budget', 'Premium'],
            'normalized_rating': [4.5, 3.8, 4.2],
            'review_count': [100, 50, 200],
            'latitude': [19.0760, 28.6139, 12.9716],
            'longitude': [72.8777, 77.2090, 77.5946],
            'popularity_score': [0.8, 0.6, 0.9],
            'composite_score': [0.75, 0.65, 0.85],
            'recency_score': [0.9, 0.7, 0.8],
            'cuisine_list': [['Italian'], ['Chinese'], ['Indian']]
        })
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Close connection if open
        if self.storage.conn:
            self.storage.disconnect()
        
        # Remove test database file
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_initialization(self):
        """Test storage initialization"""
        self.assertIsNotNone(self.storage)
        self.assertEqual(self.storage.db_path, self.test_db_path)
        self.assertIsNone(self.storage.conn)
    
    def test_connect(self):
        """Test database connection"""
        self.storage.connect()
        self.assertIsNotNone(self.storage.conn)
        self.assertIsInstance(self.storage.conn, sqlite3.Connection)
        self.storage.disconnect()
    
    def test_create_schema(self):
        """Test schema creation"""
        self.storage.connect()
        self.storage.create_schema()
        
        # Check that tables exist
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('restaurants', tables)
        self.assertIn('review_aggregations', tables)
        
        # Check that indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        self.assertTrue(any('idx_city' in idx for idx in indexes))
        self.assertTrue(any('idx_price_range' in idx for idx in indexes))
        
        self.storage.disconnect()
    
    def test_store_data(self):
        """Test storing data in database"""
        self.storage.connect()
        self.storage.create_schema()
        self.storage.store_data(self.sample_data)
        
        # Verify data was stored
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM restaurants")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, len(self.sample_data), "All records should be stored")
        self.storage.disconnect()
    
    def test_load_from_db(self):
        """Test loading data from database"""
        self.storage.connect()
        self.storage.create_schema()
        self.storage.store_data(self.sample_data)
        
        # Load data
        loaded_data = self.storage.load_from_db()
        
        self.assertIsNotNone(loaded_data)
        self.assertIsInstance(loaded_data, pd.DataFrame)
        self.assertEqual(len(loaded_data), len(self.sample_data))
        
        # Check that key columns exist
        self.assertIn('restaurant_id', loaded_data.columns)
        self.assertIn('restaurant_name', loaded_data.columns)
        self.assertIn('city', loaded_data.columns)
        
        self.storage.disconnect()
    
    def test_save_to_csv(self):
        """Test saving data to CSV"""
        test_csv_path = "phase_1_data_ingestion/data/processed/test_data.csv"
        
        self.storage.save_to_csv(self.sample_data, test_csv_path)
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_csv_path), "CSV file should be created")
        
        # Verify data can be loaded back
        loaded_data = pd.read_csv(test_csv_path)
        self.assertEqual(len(loaded_data), len(self.sample_data))
        
        # Clean up
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)
    
    def test_save_to_json(self):
        """Test saving data to JSON"""
        test_json_path = "phase_1_data_ingestion/data/processed/test_data.json"
        
        self.storage.save_to_json(self.sample_data, test_json_path)
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_json_path), "JSON file should be created")
        
        # Clean up
        if os.path.exists(test_json_path):
            os.remove(test_json_path)
    
    def test_get_storage_stats(self):
        """Test getting storage statistics"""
        self.storage.connect()
        self.storage.create_schema()
        self.storage.store_data(self.sample_data)
        
        stats = self.storage.get_storage_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_restaurants', stats)
        self.assertIn('cities', stats)
        self.assertIn('city_distribution', stats)
        self.assertIn('price_range_distribution', stats)
        self.assertIn('average_rating', stats)
        
        self.assertEqual(stats['total_restaurants'], len(self.sample_data))
        self.assertGreater(stats['cities'], 0)
        
        self.storage.disconnect()
    
    def test_context_manager(self):
        """Test context manager usage"""
        with self.storage as storage:
            self.assertIsNotNone(storage.conn)
            storage.create_schema()
            storage.store_data(self.sample_data)
        
        # Connection should be closed
        self.assertIsNone(self.storage.conn)
    
    def test_query_filtering(self):
        """Test querying with filters"""
        self.storage.connect()
        self.storage.create_schema()
        self.storage.store_data(self.sample_data)
        
        # Query by city
        query = "SELECT * FROM restaurants WHERE city = 'Mumbai'"
        filtered_data = self.storage.load_from_db(query)
        
        self.assertIsInstance(filtered_data, pd.DataFrame)
        self.assertGreater(len(filtered_data), 0)
        self.assertTrue((filtered_data['city'] == 'Mumbai').all())
        
        self.storage.disconnect()


if __name__ == '__main__':
    unittest.main()
