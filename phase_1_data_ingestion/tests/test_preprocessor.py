"""
Test cases for Data Preprocessor Module
"""

import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessor import ZomatoDataPreprocessor


class TestZomatoDataPreprocessor(unittest.TestCase):
    """Test cases for ZomatoDataPreprocessor"""
    
    def setUp(self):
        """Set up test fixtures with cleaned sample data"""
        self.cleaned_data = pd.DataFrame({
            'restaurant_id': [1, 2, 3, 4, 5],
            'restaurant_name': ['Restaurant A', 'Restaurant B', 'Restaurant C', 'Restaurant D', 'Restaurant E'],
            'city': ['Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Delhi'],
            'cuisine': ['Italian', 'Chinese, Indian', 'Indian', 'Italian, Continental', 'Chinese'],
            'rating': [4.5, 3.8, 4.2, 4.0, 3.5],
            'price': ['$$', '$$$', '$', '$$', '$$$'],
            'review_count': [100, 50, 200, 75, 150],
            'latitude': [19.0760, 28.6139, 12.9716, 19.0760, 28.6139],
            'longitude': [72.8777, 77.2090, 77.5946, 72.8777, 77.2090]
        })
    
    def test_initialization(self):
        """Test preprocessor initialization"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        self.assertIsNotNone(preprocessor)
        self.assertIsNotNone(preprocessor.cleaned_data)
        self.assertIsNone(preprocessor.processed_data)
    
    def test_engineer_features(self):
        """Test feature engineering"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._engineer_features()
        
        # Check that restaurant_id exists
        self.assertIn('restaurant_id', preprocessor.processed_data.columns)
        # Check that restaurant_name exists
        self.assertIn('restaurant_name', preprocessor.processed_data.columns)
        # Check that city exists
        self.assertIn('city', preprocessor.processed_data.columns)
    
    def test_categorize_price_range(self):
        """Test price range categorization"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._categorize_price_range()
        
        # Check that price_range column exists
        self.assertIn('price_range', preprocessor.processed_data.columns)
        
        # Check that values are in expected categories
        valid_categories = ['Budget', 'Mid-Range', 'Premium', 'Luxury']
        price_ranges = preprocessor.processed_data['price_range'].unique()
        for price_range in price_ranges:
            self.assertIn(price_range, valid_categories,
                          f"Price range {price_range} should be one of {valid_categories}")
    
    def test_normalize_ratings(self):
        """Test rating normalization"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._normalize_ratings()
        
        # Check that normalized_rating exists
        self.assertIn('normalized_rating', preprocessor.processed_data.columns)
        
        # Check that ratings are between 0 and 5
        ratings = preprocessor.processed_data['normalized_rating']
        self.assertTrue((ratings >= 0).all() and (ratings <= 5).all(),
                       "Normalized ratings should be between 0 and 5")
    
    def test_aggregate_reviews(self):
        """Test review aggregation"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._aggregate_reviews()
        
        # Check that review_count exists
        self.assertIn('review_count', preprocessor.processed_data.columns)
        
        # Check that recency_score exists
        self.assertIn('recency_score', preprocessor.processed_data.columns)
        
        # Check that recency_score is between 0 and 1
        recency_scores = preprocessor.processed_data['recency_score']
        self.assertTrue((recency_scores >= 0).all() and (recency_scores <= 1).all(),
                       "Recency scores should be between 0 and 1")
    
    def test_calculate_popularity_metrics(self):
        """Test popularity metric calculation"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._normalize_ratings()
        preprocessor._aggregate_reviews()
        preprocessor._calculate_popularity_metrics()
        
        # Check that popularity_score exists
        self.assertIn('popularity_score', preprocessor.processed_data.columns)
        
        # Check that popularity_score is between 0 and 1
        popularity_scores = preprocessor.processed_data['popularity_score']
        self.assertTrue((popularity_scores >= 0).all() and (popularity_scores <= 1).all(),
                       "Popularity scores should be between 0 and 1")
    
    def test_encode_cuisines(self):
        """Test cuisine encoding"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._encode_cuisines()
        
        # Check that primary_cuisine exists
        self.assertIn('primary_cuisine', preprocessor.processed_data.columns)
        
        # Check that cuisine_list exists
        self.assertIn('cuisine_list', preprocessor.processed_data.columns)
        
        # Check that cuisine_count exists
        self.assertIn('cuisine_count', preprocessor.processed_data.columns)
        
        # Check that cuisine_list contains lists
        cuisine_lists = preprocessor.processed_data['cuisine_list']
        self.assertTrue(all(isinstance(cuisine_list, list) for cuisine_list in cuisine_lists),
                       "Cuisine lists should be lists")
    
    def test_process_geospatial(self):
        """Test geospatial processing"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._process_geospatial()
        
        # Check that latitude and longitude exist
        self.assertIn('latitude', preprocessor.processed_data.columns)
        self.assertIn('longitude', preprocessor.processed_data.columns)
        
        # Check that coordinates are in valid ranges
        latitudes = preprocessor.processed_data['latitude']
        longitudes = preprocessor.processed_data['longitude']
        
        self.assertTrue((latitudes >= -90).all() and (latitudes <= 90).all(),
                       "Latitudes should be between -90 and 90")
        self.assertTrue((longitudes >= -180).all() and (longitudes <= 180).all(),
                       "Longitudes should be between -180 and 180")
    
    def test_create_composite_scores(self):
        """Test composite score creation"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor._normalize_ratings()
        preprocessor._aggregate_reviews()
        preprocessor._calculate_popularity_metrics()
        preprocessor._create_composite_scores()
        
        # Check that composite_score exists
        self.assertIn('composite_score', preprocessor.processed_data.columns)
        
        # Check that composite_score is between 0 and 1
        composite_scores = preprocessor.processed_data['composite_score']
        self.assertTrue((composite_scores >= 0).all() and (composite_scores <= 1).all(),
                       "Composite scores should be between 0 and 1")
    
    def test_complete_preprocess(self):
        """Test complete preprocessing process"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        processed = preprocessor.preprocess()
        
        self.assertIsNotNone(processed)
        self.assertIsInstance(processed, pd.DataFrame)
        self.assertGreater(len(processed), 0, "Processed data should not be empty")
        
        # Check that key columns exist
        required_columns = [
            'restaurant_id', 'restaurant_name', 'city', 'price_range',
            'normalized_rating', 'review_count', 'popularity_score',
            'composite_score', 'primary_cuisine'
        ]
        for col in required_columns:
            self.assertIn(col, processed.columns, f"Column {col} should exist after preprocessing")
    
    def test_get_preprocessing_stats(self):
        """Test getting preprocessing statistics"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        preprocessor.preprocess()
        
        stats = preprocessor.get_preprocessing_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_restaurants', stats)
        self.assertGreater(stats['total_restaurants'], 0)
    
    def test_get_processed_data(self):
        """Test getting processed data"""
        preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
        self.assertIsNone(preprocessor.get_processed_data())
        
        preprocessor.preprocess()
        processed = preprocessor.get_processed_data()
        self.assertIsNotNone(processed)
        self.assertIsInstance(processed, pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
