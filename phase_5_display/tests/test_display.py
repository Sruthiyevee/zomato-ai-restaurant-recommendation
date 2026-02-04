"""
Unit tests for DisplayManager
Verifies formatting and output rendering
"""

import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from display_manager import DisplayManager

class TestDisplayManager(unittest.TestCase):
    
    def setUp(self):
        self.display = DisplayManager()
        
    def test_star_rating_calculation(self):
        """Test conversion of numeric rating to stars"""
        self.assertEqual(self.display._get_star_rating(5.0), "★★★★★")
        self.assertEqual(self.display._get_star_rating(4.5), "★★★★½")
        self.assertEqual(self.display._get_star_rating(4.0), "★★★★☆")
        self.assertEqual(self.display._get_star_rating(3.5), "★★★½☆")
        self.assertEqual(self.display._get_star_rating(0.0), "☆☆☆☆☆")
        
        # Test invalid inputs handled gracefully
        self.assertEqual(self.display._get_star_rating("invalid"), "☆☆☆☆☆")

    def test_price_formatting(self):
        """Test price range formatting"""
        self.assertEqual(self.display.format_price("Budget"), "Budget ($)")
        self.assertEqual(self.display.format_price("Mid-Range"), "Mid-Range ($$)")
        self.assertEqual(self.display.format_price("Premium"), "Premium ($$$)")
        self.assertEqual(self.display.format_price("Luxury"), "Luxury ($$$$)")
        self.assertEqual(self.display.format_price("Unknown"), "Unknown")

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_recommendations_rendering(self, mock_stdout):
        """Test rendering of recommendation list"""
        recs = [
            {
                'restaurant_name': 'Test Rest',
                'cuisine': 'Test Cuisine',
                'rating': 4.5,
                'review_count': 100,
                'price_range': 'Budget',
                'reasoning': 'Because it represents a test.',
                'key_features': ['Feature1', 'Feature2']
            }
        ]
        
        self.display.display_recommendations(recs, "Test City", "Budget")
        
        output = mock_stdout.getvalue()
        
        # Verify Key Information Present
        self.assertIn("Test City", output)
        self.assertIn("Budget ($)", output)
        self.assertIn("TEST REST", output) # Uppercase name
        self.assertIn("Test Cuisine", output)
        self.assertIn("★★★★½", output)
        self.assertIn("Feature1, Feature2", output)
        self.assertIn("Because it represents a test", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_error(self, mock_stdout):
        """Test error display"""
        self.display.display_error("Something went wrong")
        output = mock_stdout.getvalue()
        self.assertIn("ERROR:", output)
        self.assertIn("Something went wrong", output)

if __name__ == '__main__':
    unittest.main()
