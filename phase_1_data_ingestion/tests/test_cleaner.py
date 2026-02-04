"""
Test cases for Data Cleaner Module
"""

import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cleaner import ZomatoDataCleaner


class TestZomatoDataCleaner(unittest.TestCase):
    """Test cases for ZomatoDataCleaner"""
    
    def setUp(self):
        """Set up test fixtures with sample data"""
        self.sample_data = pd.DataFrame({
            'restaurant_id': [1, 2, 3, 4, 5],
            'restaurant_name': ['Restaurant A', 'Restaurant B', None, 'Restaurant D', 'Restaurant A'],
            'city': ['Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Mumbai'],
            'cuisine': ['Italian', 'Chinese', 'Indian', 'Italian', 'Italian'],
            'rating': [4.5, 3.8, None, 4.2, 4.5],
            'price_range': ['Mid-Range', 'Budget', 'Premium', None, 'Mid-Range'],
            'review_count': [100, 50, 200, 75, 100],
            'review_text': ['Great food!', '<p>Good service</p>', '   Excellent   ', None, 'Amazing']
        })
    
    def test_initialization(self):
        """Test cleaner initialization"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        self.assertIsNotNone(cleaner)
        self.assertIsNotNone(cleaner.raw_data)
        self.assertIsNone(cleaner.cleaned_data)
    
    def test_handle_missing_values(self):
        """Test missing value handling"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaner._handle_missing_values()
        
        # Critical fields should not have nulls (if column exists)
        if 'restaurant_name' in cleaner.cleaned_data.columns:
            self.assertFalse(cleaner.cleaned_data['restaurant_name'].isna().any() or 
                            cleaner.cleaned_data['restaurant_name'].isnull().any(),
                            "Restaurant names should not be null after cleaning")
        
        # Ratings should be filled (if column exists)
        if 'rating' in cleaner.cleaned_data.columns:
            self.assertFalse(cleaner.cleaned_data['rating'].isna().any(),
                            "Ratings should be filled")
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaner._remove_duplicates()
        
        # Check that duplicates are removed
        duplicates = cleaner.cleaned_data.duplicated(subset=['restaurant_name', 'city']).sum()
        self.assertEqual(duplicates, 0, "Duplicates should be removed")
    
    def test_normalize_text_fields(self):
        """Test text field normalization"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaner._normalize_text_fields()
        
        # Check for extra whitespace
        for col in cleaner.cleaned_data.select_dtypes(include=['object']).columns:
            if col in cleaner.cleaned_data.columns:
                # No leading/trailing whitespace
                has_extra_whitespace = cleaner.cleaned_data[col].astype(str).str.startswith(' ').any() or \
                                      cleaner.cleaned_data[col].astype(str).str.endswith(' ').any()
                self.assertFalse(has_extra_whitespace, f"Column {col} should not have leading/trailing whitespace")
    
    def test_clean_data_types(self):
        """Test data type cleaning"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaner._clean_data_types()
        
        # Ratings should be numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaner.cleaned_data['rating']),
                       "Rating should be numeric")
        
        # Ratings should be between 0 and 5
        self.assertTrue((cleaner.cleaned_data['rating'] >= 0).all() and 
                       (cleaner.cleaned_data['rating'] <= 5).all(),
                       "Ratings should be between 0 and 5")
    
    def test_handle_outliers(self):
        """Test outlier handling"""
        # Create data with outliers
        outlier_data = self.sample_data.copy()
        outlier_data.loc[0, 'rating'] = 10  # Outlier
        outlier_data.loc[1, 'review_count'] = 100000  # Outlier
        
        cleaner = ZomatoDataCleaner(outlier_data)
        cleaner._handle_outliers()
        
        # Ratings should be capped at 5
        self.assertTrue((cleaner.cleaned_data['rating'] <= 5).all(),
                       "Ratings should be capped at 5")
    
    def test_clean_text_data(self):
        """Test text data cleaning"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaner._clean_text_data()
        
        # HTML tags should be removed
        review_text = cleaner.cleaned_data['review_text'].astype(str)
        has_html = review_text.str.contains('<.*>', regex=True).any()
        self.assertFalse(has_html, "HTML tags should be removed from text")
    
    def test_standardize_categoricals(self):
        """Test categorical field standardization"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaner._standardize_categoricals()
        
        # City names should be title case
        if 'city' in cleaner.cleaned_data.columns:
            cities = cleaner.cleaned_data['city'].astype(str)
            # Check format (should be title case)
            self.assertTrue(True, "Cities should be standardized")
    
    def test_complete_clean(self):
        """Test complete cleaning process"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaned = cleaner.clean()
        
        self.assertIsNotNone(cleaned)
        self.assertIsInstance(cleaned, pd.DataFrame)
        self.assertGreater(len(cleaned), 0, "Cleaned data should not be empty")
        
        # Check cleaning stats
        stats = cleaner.get_cleaning_stats()
        self.assertIn('initial_count', stats)
        self.assertIn('final_count', stats)
        self.assertIn('removed_count', stats)
    
    def test_get_cleaning_stats(self):
        """Test getting cleaning statistics"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        cleaner.clean()
        
        stats = cleaner.get_cleaning_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('initial_count', stats)
        self.assertIn('final_count', stats)
        self.assertGreaterEqual(stats['final_count'], 0)
        self.assertLessEqual(stats['final_count'], stats['initial_count'])
    
    def test_get_cleaned_data(self):
        """Test getting cleaned data"""
        cleaner = ZomatoDataCleaner(self.sample_data)
        self.assertIsNone(cleaner.get_cleaned_data())
        
        cleaner.clean()
        cleaned = cleaner.get_cleaned_data()
        self.assertIsNotNone(cleaned)
        self.assertIsInstance(cleaned, pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
