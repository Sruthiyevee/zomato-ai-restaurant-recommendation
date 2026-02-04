"""
Test cases for Session Manager Module
"""

import unittest
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from session_manager import SessionManager, SessionState
from validator import PriceRange


class TestSessionManager(unittest.TestCase):
    """Test cases for SessionManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.session_manager = SessionManager(session_timeout_minutes=30)
    
    def test_initialization(self):
        """Test session manager initialization"""
        self.assertIsNotNone(self.session_manager)
        self.assertIsNotNone(self.session_manager.session_id)
        self.assertTrue(self.session_manager.session_id.startswith("session_"))
        self.assertEqual(self.session_manager.state, SessionState.INITIALIZED)
        self.assertIsNone(self.session_manager.current_city)
        self.assertIsNone(self.session_manager.current_price_range)
        self.assertEqual(len(self.session_manager.query_history), 0)
    
    def test_set_user_input(self):
        """Test setting user input"""
        self.session_manager.set_user_input("Mumbai", PriceRange.MID_RANGE)
        
        self.assertEqual(self.session_manager.current_city, "Mumbai")
        self.assertEqual(self.session_manager.current_price_range, PriceRange.MID_RANGE)
        self.assertEqual(self.session_manager.state, SessionState.INPUT_COLLECTED)
    
    def test_get_user_input(self):
        """Test getting user input"""
        # Initially should be None
        result = self.session_manager.get_user_input()
        self.assertIsNone(result)
        
        # After setting input
        self.session_manager.set_user_input("Delhi", PriceRange.PREMIUM)
        result = self.session_manager.get_user_input()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['city'], "Delhi")
        self.assertEqual(result['price_range'], PriceRange.PREMIUM)
    
    def test_start_processing(self):
        """Test starting processing state"""
        self.session_manager.set_user_input("Bangalore", PriceRange.BUDGET)
        self.session_manager.start_processing()
        
        self.assertEqual(self.session_manager.state, SessionState.PROCESSING)
    
    def test_complete_query(self):
        """Test completing a query"""
        self.session_manager.set_user_input("Chennai", PriceRange.LUXURY)
        self.session_manager.start_processing()
        
        results = {'recommendations': ['Restaurant A', 'Restaurant B']}
        self.session_manager.complete_query(results)
        
        self.assertEqual(self.session_manager.state, SessionState.COMPLETED)
        self.assertEqual(len(self.session_manager.query_history), 1)
        
        history_entry = self.session_manager.query_history[0]
        self.assertEqual(history_entry['city'], "Chennai")
        self.assertEqual(history_entry['price_range'], PriceRange.LUXURY.value)
        self.assertEqual(history_entry['results'], results)
        self.assertIn('timestamp', history_entry)
    
    def test_complete_query_no_results(self):
        """Test completing query without results"""
        self.session_manager.set_user_input("Mumbai", PriceRange.MID_RANGE)
        self.session_manager.complete_query()
        
        self.assertEqual(self.session_manager.state, SessionState.COMPLETED)
        self.assertEqual(len(self.session_manager.query_history), 1)
        self.assertIsNone(self.session_manager.query_history[0]['results'])
    
    def test_set_error(self):
        """Test setting error state"""
        self.session_manager.set_user_input("Delhi", PriceRange.PREMIUM)
        self.session_manager.set_error("Test error message")
        
        self.assertEqual(self.session_manager.state, SessionState.ERROR)
        self.assertEqual(len(self.session_manager.query_history), 1)
        
        history_entry = self.session_manager.query_history[0]
        self.assertEqual(history_entry['error'], "Test error message")
    
    def test_reset_for_new_query(self):
        """Test resetting for new query"""
        self.session_manager.set_user_input("Bangalore", PriceRange.BUDGET)
        self.session_manager.complete_query()
        
        # Reset
        self.session_manager.reset_for_new_query()
        
        self.assertIsNone(self.session_manager.current_city)
        self.assertIsNone(self.session_manager.current_price_range)
        self.assertEqual(self.session_manager.state, SessionState.INITIALIZED)
        # History should be preserved
        self.assertEqual(len(self.session_manager.query_history), 1)
    
    def test_is_expired(self):
        """Test session expiration check"""
        # New session should not be expired
        self.assertFalse(self.session_manager.is_expired())
        
        # Create session with very short timeout
        short_session = SessionManager(session_timeout_minutes=0.001)  # 0.06 seconds
        time.sleep(0.1)  # Wait longer than timeout
        self.assertTrue(short_session.is_expired())
    
    def test_get_session_info(self):
        """Test getting session information"""
        info = self.session_manager.get_session_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('session_id', info)
        self.assertIn('state', info)
        self.assertIn('created_at', info)
        self.assertIn('last_activity', info)
        self.assertIn('is_expired', info)
        self.assertIn('query_count', info)
        self.assertIn('current_city', info)
        self.assertIn('current_price_range', info)
        
        self.assertEqual(info['state'], SessionState.INITIALIZED.value)
        self.assertEqual(info['query_count'], 0)
    
    def test_get_query_history(self):
        """Test getting query history"""
        # Initially empty
        history = self.session_manager.get_query_history()
        self.assertEqual(len(history), 0)
        
        # Add queries
        self.session_manager.set_user_input("Mumbai", PriceRange.MID_RANGE)
        self.session_manager.complete_query()
        
        self.session_manager.reset_for_new_query()
        self.session_manager.set_user_input("Delhi", PriceRange.PREMIUM)
        self.session_manager.complete_query()
        
        history = self.session_manager.get_query_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['city'], "Mumbai")
        self.assertEqual(history[1]['city'], "Delhi")
    
    def test_clear_history(self):
        """Test clearing query history"""
        self.session_manager.set_user_input("Mumbai", PriceRange.MID_RANGE)
        self.session_manager.complete_query()
        
        self.assertEqual(len(self.session_manager.query_history), 1)
        
        self.session_manager.clear_history()
        self.assertEqual(len(self.session_manager.query_history), 0)
    
    def test_get_last_query(self):
        """Test getting last query"""
        # Initially None
        last_query = self.session_manager.get_last_query()
        self.assertIsNone(last_query)
        
        # After adding queries
        self.session_manager.set_user_input("Mumbai", PriceRange.MID_RANGE)
        self.session_manager.complete_query()
        
        last_query = self.session_manager.get_last_query()
        self.assertIsNotNone(last_query)
        self.assertEqual(last_query['city'], "Mumbai")
        
        # Add another query
        self.session_manager.reset_for_new_query()
        self.session_manager.set_user_input("Delhi", PriceRange.PREMIUM)
        self.session_manager.complete_query()
        
        last_query = self.session_manager.get_last_query()
        self.assertEqual(last_query['city'], "Delhi")
    
    def test_multiple_queries(self):
        """Test handling multiple queries in session"""
        # First query
        self.session_manager.set_user_input("Mumbai", PriceRange.BUDGET)
        self.session_manager.complete_query({'count': 5})
        
        # Second query
        self.session_manager.reset_for_new_query()
        self.session_manager.set_user_input("Delhi", PriceRange.PREMIUM)
        self.session_manager.complete_query({'count': 3})
        
        # Verify history
        history = self.session_manager.get_query_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['city'], "Mumbai")
        self.assertEqual(history[1]['city'], "Delhi")


if __name__ == '__main__':
    unittest.main()
