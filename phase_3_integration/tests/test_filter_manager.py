"""
Test cases for Filter Manager Module
"""

import unittest
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filter_manager import FilterManager, PriceRange


class TestFilterManager(unittest.TestCase):
    """Test cases for FilterManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_data = pd.DataFrame({
            'restaurant_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'restaurant_name': ['Restaurant A', 'Restaurant B', 'Restaurant C', 'Restaurant D', 'Restaurant E',
                               'Restaurant F', 'Restaurant G', 'Restaurant H', 'Restaurant I', 'Restaurant J'],
            'city': ['Mumbai', 'Mumbai', 'Delhi', 'Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Delhi', 'Mumbai', 'Bangalore'],
            'price_range': ['Budget', 'Mid-Range', 'Premium', 'Budget', 'Mid-Range', 'Premium', 'Luxury', 'Budget', 'Mid-Range', 'Premium'],
            'normalized_rating': [4.5, 3.8, 4.2, 4.0, 3.5, 4.8, 3.2, 4.3, 3.9, 4.1],
            'review_count': [100, 50, 200, 75, 30, 150, 25, 120, 60, 180],
            'primary_cuisine': ['Italian', 'Chinese', 'Indian', 'Italian', 'Chinese', 'Indian', 'Italian', 'Indian', 'Chinese', 'Italian'],
            'composite_score': [0.8, 0.6, 0.9, 0.7, 0.5, 0.95, 0.4, 0.85, 0.65, 0.75]
        })
        self.filter_manager = FilterManager(self.sample_data)
    
    def test_initialization(self):
        """Test filter manager initialization"""
        self.assertIsNotNone(self.filter_manager)
        self.assertIsNotNone(self.filter_manager.data)
        self.assertIsNone(self.filter_manager.filtered_data)
    
    def test_apply_geographic_filter(self):
        """Test geographic filtering by city"""
        filtered = self.filter_manager.apply_geographic_filter("Mumbai")
        
        self.assertIsNotNone(filtered)
        self.assertGreater(len(filtered), 0)
        self.assertTrue((filtered['city'] == 'Mumbai').all())
    
    def test_apply_geographic_filter_case_insensitive(self):
        """Test geographic filter is case insensitive"""
        filtered1 = self.filter_manager.apply_geographic_filter("mumbai")
        filtered2 = self.filter_manager.apply_geographic_filter("Mumbai")
        
        self.assertEqual(len(filtered1), len(filtered2))
    
    def test_apply_geographic_filter_no_results(self):
        """Test geographic filter with no matching city"""
        filtered = self.filter_manager.apply_geographic_filter("Pune")
        
        self.assertIsNotNone(filtered)
        self.assertEqual(len(filtered), 0)
    
    def test_apply_price_filter(self):
        """Test price range filtering"""
        filtered = self.filter_manager.apply_price_filter(PriceRange.BUDGET)
        
        self.assertIsNotNone(filtered)
        self.assertGreater(len(filtered), 0)
        self.assertTrue((filtered['price_range'] == 'Budget').all())
    
    def test_apply_price_filter_with_data(self):
        """Test price filter with provided data"""
        city_filtered = self.filter_manager.apply_geographic_filter("Mumbai")
        price_filtered = self.filter_manager.apply_price_filter(PriceRange.MID_RANGE, city_filtered)
        
        self.assertIsNotNone(price_filtered)
        self.assertTrue((price_filtered['price_range'] == 'Mid-Range').all())
        self.assertTrue((price_filtered['city'] == 'Mumbai').all())
    
    def test_apply_quality_filter(self):
        """Test quality filtering (rating and reviews)"""
        filtered = self.filter_manager.apply_quality_filter(
            min_rating=4.0,
            min_reviews=50
        )
        
        self.assertIsNotNone(filtered)
        if len(filtered) > 0:
            self.assertTrue((filtered['normalized_rating'] >= 4.0).all())
            self.assertTrue((filtered['review_count'] >= 50).all())
    
    def test_filter_restaurants_complete(self):
        """Test complete filtering pipeline"""
        filtered = self.filter_manager.filter_restaurants(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE,
            min_rating=3.5,
            min_reviews=30
        )
        
        self.assertIsNotNone(filtered)
        if len(filtered) > 0:
            self.assertTrue((filtered['city'] == 'Mumbai').all())
            self.assertTrue((filtered['price_range'] == 'Mid-Range').all())
            self.assertTrue((filtered['normalized_rating'] >= 3.5).all())
            self.assertTrue((filtered['review_count'] >= 30).all())
    
    def test_filter_restaurants_no_results(self):
        """Test filtering with no matching results"""
        filtered = self.filter_manager.filter_restaurants(
            city="Pune",
            price_range=PriceRange.LUXURY,
            min_rating=5.0,
            min_reviews=1000
        )
        
        self.assertIsNotNone(filtered)
        self.assertEqual(len(filtered), 0)
    
    def test_optimize_candidates(self):
        """Test candidate optimization"""
        filtered = self.filter_manager.filter_restaurants("Mumbai", PriceRange.MID_RANGE)
        optimized = self.filter_manager.optimize_candidates(
            data=filtered,
            max_candidates=3
        )
        
        self.assertIsNotNone(optimized)
        self.assertLessEqual(len(optimized), 3)
    
    def test_optimize_candidates_with_diversity(self):
        """Test candidate optimization with diversity"""
        filtered = self.filter_manager.filter_restaurants("Mumbai", PriceRange.MID_RANGE)
        optimized = self.filter_manager.optimize_candidates(
            data=filtered,
            max_candidates=5,
            ensure_diversity=True
        )
        
        self.assertIsNotNone(optimized)
        self.assertLessEqual(len(optimized), 5)
    
    def test_get_filter_stats(self):
        """Test getting filter statistics"""
        self.filter_manager.filter_restaurants("Mumbai", PriceRange.MID_RANGE)
        stats = self.filter_manager.get_filter_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('initial_count', stats)
        self.assertIn('final_count', stats)
        self.assertIn('filtered_out', stats)
        self.assertIn('retention_rate', stats)
    
    def test_get_filtered_data(self):
        """Test getting filtered data"""
        self.assertIsNone(self.filter_manager.get_filtered_data())
        
        self.filter_manager.filter_restaurants("Mumbai", PriceRange.MID_RANGE)
        filtered = self.filter_manager.get_filtered_data()
        
        self.assertIsNotNone(filtered)
        self.assertIsInstance(filtered, pd.DataFrame)
    
    def test_empty_data(self):
        """Test handling of empty data"""
        empty_manager = FilterManager(pd.DataFrame())
        filtered = empty_manager.apply_geographic_filter("Mumbai")
        
        self.assertIsNotNone(filtered)
        self.assertEqual(len(filtered), 0)


if __name__ == '__main__':
    unittest.main()
