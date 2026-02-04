"""
Integration tests for Phase 2 components
Tests interaction between validator, CLI handler, and session manager
"""

import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validator import InputValidator, PriceRange
from cli_handler import CLIHandler
from session_manager import SessionManager, SessionState


class TestPhase2Integration(unittest.TestCase):
    """Integration tests for Phase 2"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.available_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai']
        self.validator = InputValidator(available_cities=self.available_cities)
        self.cli_handler = CLIHandler(validator=self.validator)
        self.session_manager = SessionManager()
    
    def test_validator_cli_integration(self):
        """Test integration between validator and CLI handler"""
        # CLI handler should use validator
        self.assertEqual(self.cli_handler.validator, self.validator)
        
        # Validator should have correct cities
        cities = self.validator.get_available_cities()
        self.assertIn('Mumbai', cities)
    
    def test_session_manager_with_user_input(self):
        """Test session manager with user input flow"""
        # Simulate user input collection
        user_input = {
            'city': 'Mumbai',
            'price_range': PriceRange.MID_RANGE
        }
        
        # Set in session
        self.session_manager.set_user_input(
            user_input['city'],
            user_input['price_range']
        )
        
        # Verify session state
        self.assertEqual(self.session_manager.state, SessionState.INPUT_COLLECTED)
        retrieved_input = self.session_manager.get_user_input()
        self.assertEqual(retrieved_input['city'], 'Mumbai')
        self.assertEqual(retrieved_input['price_range'], PriceRange.MID_RANGE)
    
    def test_complete_flow_simulation(self):
        """Test complete flow simulation"""
        # Step 1: User provides input (simulated)
        city = "Delhi"
        price_range = PriceRange.PREMIUM
        
        # Step 2: Validate input
        is_valid_city, normalized_city, _ = self.validator.validate_city(city)
        self.assertTrue(is_valid_city)
        
        is_valid_price, validated_price, _ = self.validator.validate_price_range("3")
        self.assertTrue(is_valid_price)
        
        # Step 3: Store in session
        self.session_manager.set_user_input(normalized_city, validated_price)
        self.assertEqual(self.session_manager.state, SessionState.INPUT_COLLECTED)
        
        # Step 4: Start processing
        self.session_manager.start_processing()
        self.assertEqual(self.session_manager.state, SessionState.PROCESSING)
        
        # Step 5: Complete query
        results = {'recommendations': ['Restaurant A', 'Restaurant B']}
        self.session_manager.complete_query(results)
        self.assertEqual(self.session_manager.state, SessionState.COMPLETED)
        
        # Verify history
        history = self.session_manager.get_query_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['city'], normalized_city)
    
    def test_error_handling_flow(self):
        """Test error handling in complete flow"""
        # Invalid city
        is_valid, normalized, suggestions = self.validator.validate_city("InvalidCity")
        self.assertFalse(is_valid)
        
        # Valid price range
        is_valid_price, price_range, _ = self.validator.validate_price_range("2")
        self.assertTrue(is_valid_price)
        
        # If we had invalid input, session would handle error
        self.session_manager.set_user_input("Delhi", PriceRange.MID_RANGE)
        self.session_manager.set_error("Invalid city provided")
        
        self.assertEqual(self.session_manager.state, SessionState.ERROR)
        history = self.session_manager.get_query_history()
        self.assertEqual(len(history), 1)
        self.assertIn('error', history[0])
    
    def test_multiple_queries_in_session(self):
        """Test multiple queries in same session"""
        # First query
        self.session_manager.set_user_input("Mumbai", PriceRange.BUDGET)
        self.session_manager.complete_query({'count': 5})
        
        # Second query
        self.session_manager.reset_for_new_query()
        self.session_manager.set_user_input("Bangalore", PriceRange.PREMIUM)
        self.session_manager.complete_query({'count': 3})
        
        # Verify both in history
        history = self.session_manager.get_query_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['city'], "Mumbai")
        self.assertEqual(history[1]['city'], "Bangalore")
    
    def test_validator_price_range_mapping(self):
        """Test various price range input formats"""
        # Test numeric
        is_valid, price_range, _ = self.validator.validate_price_range("1")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.BUDGET)
        
        # Test text variations
        is_valid, price_range, _ = self.validator.validate_price_range("budget")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.BUDGET)
        
        is_valid, price_range, _ = self.validator.validate_price_range("mid-range")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.MID_RANGE)
        
        is_valid, price_range, _ = self.validator.validate_price_range("premium")
        self.assertTrue(is_valid)
        self.assertEqual(price_range, PriceRange.PREMIUM)
    
    def test_city_fuzzy_matching(self):
        """Test fuzzy matching for city names"""
        # Close match should provide suggestions
        is_valid, normalized, suggestions = self.validator.validate_city("Mumbay")
        # Should either match or provide suggestions
        self.assertTrue(is_valid or (suggestions is not None and len(suggestions) > 0))
    
    def test_session_info_completeness(self):
        """Test session info contains all required fields"""
        self.session_manager.set_user_input("Chennai", PriceRange.LUXURY)
        info = self.session_manager.get_session_info()
        
        required_fields = [
            'session_id', 'state', 'created_at', 'last_activity',
            'is_expired', 'query_count', 'current_city', 'current_price_range'
        ]
        
        for field in required_fields:
            self.assertIn(field, info, f"Session info missing field: {field}")


if __name__ == '__main__':
    unittest.main()
