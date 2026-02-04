"""
Test cases for Input Validator Module
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validator import InputValidator, PriceRange


class TestInputValidator(unittest.TestCase):
    """Test cases for InputValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.available_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
        self.validator = InputValidator(available_cities=self.available_cities)
    
    def test_initialization(self):
        """Test validator initialization"""
        self.assertIsNotNone(self.validator)
        self.assertEqual(len(self.validator.available_cities), 5)
        self.assertEqual(len(self.validator.price_ranges), 4)
    
    def test_validate_city_exact_match(self):
        """Test city validation with exact match"""
        is_valid, normalized, suggestions = self.validator.validate_city("Mumbai")
        self.assertTrue(is_valid)
        self.assertEqual(normalized, "Mumbai")
        self.assertIsNone(suggestions)
    
    def test_validate_city_case_insensitive(self):
        """Test city validation is case insensitive"""
        is_valid, normalized, suggestions = self.validator.validate_city("mumbai")
        self.assertTrue(is_valid)
        self.assertEqual(normalized, "Mumbai")
        
        is_valid, normalized, suggestions = self.validator.validate_city("MUMBAI")
        self.assertTrue(is_valid)
        self.assertEqual(normalized, "Mumbai")
    
    def test_validate_city_not_found(self):
        """Test city validation with non-existent city"""
        is_valid, normalized, suggestions = self.validator.validate_city("Pune")
        self.assertFalse(is_valid)
        self.assertIsNone(normalized)
        self.assertIsNotNone(suggestions)  # Should provide suggestions
    
    def test_validate_city_empty_input(self):
        """Test city validation with empty input"""
        is_valid, normalized, suggestions = self.validator.validate_city("")
        self.assertFalse(is_valid)
        self.assertIsNone(normalized)
        self.assertIsNone(suggestions)
    
    def test_validate_city_whitespace(self):
        """Test city validation handles whitespace"""
        is_valid, normalized, suggestions = self.validator.validate_city("  Mumbai  ")
        self.assertTrue(is_valid)
        self.assertEqual(normalized, "Mumbai")
    
    def test_validate_price_range_numeric(self):
        """Test price range validation with numeric input"""
        is_valid, price_range, error = self.validator.validate_price_range("1")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.BUDGET)
        self.assertIsNone(error)
        
        is_valid, price_range, error = self.validator.validate_price_range("2")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.MID_RANGE)
        
        is_valid, price_range, error = self.validator.validate_price_range("3")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.PREMIUM)
        
        is_valid, price_range, error = self.validator.validate_price_range("4")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.LUXURY)
    
    def test_validate_price_range_text(self):
        """Test price range validation with text input"""
        is_valid, price_range, error = self.validator.validate_price_range("Budget")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.BUDGET)
        
        is_valid, price_range, error = self.validator.validate_price_range("mid-range")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.MID_RANGE)
        
        is_valid, price_range, error = self.validator.validate_price_range("PREMIUM")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.PREMIUM)
    
    def test_validate_price_range_invalid(self):
        """Test price range validation with invalid input"""
        is_valid, price_range, error = self.validator.validate_price_range("5")
        self.assertFalse(is_valid)
        self.assertIsNone(price_range)
        self.assertIsNotNone(error)
        
        is_valid, price_range, error = self.validator.validate_price_range("invalid")
        self.assertFalse(is_valid)
        self.assertIsNone(price_range)
        self.assertIsNotNone(error)
    
    def test_validate_price_range_empty(self):
        """Test price range validation with empty input"""
        is_valid, price_range, error = self.validator.validate_price_range("")
        self.assertFalse(is_valid)
        self.assertIsNone(price_range)
        self.assertIsNotNone(error)
    
    def test_get_price_range_options(self):
        """Test getting price range options"""
        options = self.validator.get_price_range_options()
        
        self.assertIsInstance(options, list)
        self.assertEqual(len(options), 4)
        
        for option in options:
            self.assertIn('number', option)
            self.assertIn('value', option)
            self.assertIn('description', option)
            self.assertIn(option['value'], [pr.value for pr in PriceRange])
    
    def test_update_available_cities(self):
        """Test updating available cities"""
        new_cities = ['Pune', 'Hyderabad', 'Jaipur']
        self.validator.update_available_cities(new_cities)
        
        self.assertEqual(len(self.validator.available_cities), 3)
        self.assertIn('pune', self.validator.available_cities)
    
    def test_get_available_cities(self):
        """Test getting available cities"""
        cities = self.validator.get_available_cities()
        
        self.assertIsInstance(cities, list)
        self.assertEqual(len(cities), 5)
        # Should be in title case
        self.assertEqual(cities[0], "Mumbai")
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching for city names"""
        # Test with typo
        is_valid, normalized, suggestions = self.validator.validate_city("Mumbay")
        # Should provide suggestions even if not exact match
        self.assertIsNotNone(suggestions or normalized)
    
    def test_calculate_similarity(self):
        """Test similarity calculation"""
        similarity = self.validator._calculate_similarity("mumbai", "mumbai")
        self.assertEqual(similarity, 1.0)
        
        similarity = self.validator._calculate_similarity("mumbai", "delhi")
        self.assertLess(similarity, 1.0)
        self.assertGreaterEqual(similarity, 0.0)
    
    def test_no_available_cities(self):
        """Test validator with no available cities"""
        validator = InputValidator(available_cities=None)
        is_valid, normalized, suggestions = validator.validate_city("Mumbai")
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()
