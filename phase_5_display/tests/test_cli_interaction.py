"""
Unit tests for CLI Interaction
Verifies input collection and flow control
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cli import CLI

class TestCLI(unittest.TestCase):
    
    def setUp(self):
        self.cli = CLI()
        # Mock display to prevent cluttering output during tests
        self.cli.display = MagicMock()
        
    @patch('builtins.input', side_effect=['Mumbai', '2'])
    def test_get_user_inputs_success(self, mock_input):
        """Test successful input collection"""
        city, price = self.cli.get_user_inputs()
        
        self.assertEqual(city, 'Mumbai') # Should be title cased
        self.assertEqual(price, 'Mid-Range')
        
    @patch('builtins.input', side_effect=['q'])
    def test_get_user_inputs_quit_at_city(self, mock_input):
        """Test quitting at city prompt"""
        city, price = self.cli.get_user_inputs()
        self.assertIsNone(city)
        self.assertIsNone(price)
        
    @patch('builtins.input', side_effect=['Pune', 'q'])
    def test_get_user_inputs_quit_at_price(self, mock_input):
        """Test quitting at price prompt"""
        city, price = self.cli.get_user_inputs()
        self.assertIsNone(city)
        self.assertIsNone(price)
        
    @patch('builtins.input', side_effect=['', 'a', 'Bangalore', '5', 'invalid', '1'])
    def test_get_user_inputs_validation_retry(self, mock_input):
        """
        Test input validation and retries
        Sequence:
        1. '' (Empty city) -> Fail
        2. 'a' (Short city) -> Fail
        3. 'Bangalore' -> Success
        4. '5' (Invalid price) -> Fail
        5. 'invalid' (Invalid price) -> Fail
        6. '1' (Budget) -> Success
        """
        city, price = self.cli.get_user_inputs()
        
        self.assertEqual(city, 'Bangalore')
        self.assertEqual(price, 'Budget')
        
        # Verify error messages were shown
        self.assertTrue(self.cli.display.display_error.called)
        self.assertEqual(self.cli.display.display_error.call_count, 4)

    @patch('builtins.input', side_effect=['y'])
    def test_verify_continue_yes(self, mock_input):
        """Test continue with 'y'"""
        self.assertTrue(self.cli.verify_continue())

    @patch('builtins.input', side_effect=['n'])
    def test_verify_continue_no(self, mock_input):
        """Test exit with 'n'"""
        self.assertFalse(self.cli.verify_continue())

if __name__ == '__main__':
    unittest.main()
