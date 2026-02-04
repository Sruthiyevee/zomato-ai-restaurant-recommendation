"""
Test cases for CLI Handler Module
"""

import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli_handler import CLIHandler
from validator import InputValidator, PriceRange


class TestCLIHandler(unittest.TestCase):
    """Test cases for CLIHandler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.available_cities = ['Mumbai', 'Delhi', 'Bangalore']
        self.validator = InputValidator(available_cities=self.available_cities)
        self.cli_handler = CLIHandler(validator=self.validator)
    
    def test_initialization(self):
        """Test CLI handler initialization"""
        self.assertIsNotNone(self.cli_handler)
        self.assertEqual(self.cli_handler.validator, self.validator)
        self.assertEqual(self.cli_handler.max_retries, 3)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_welcome(self, mock_stdout):
        """Test welcome message display"""
        self.cli_handler.display_welcome()
        output = mock_stdout.getvalue()
        self.assertIn("ZOMATO", output)
        self.assertIn("Welcome", output)
    
    @patch('builtins.input', return_value='Mumbai')
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_city_valid(self, mock_stdout, mock_input):
        """Test collecting valid city input"""
        city = self.cli_handler.collect_city()
        self.assertEqual(city, "Mumbai")
        output = mock_stdout.getvalue()
        self.assertIn("City selected", output)
    
    @patch('builtins.input', side_effect=['InvalidCity', 'Mumbai'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_city_with_retry(self, mock_stdout, mock_input):
        """Test collecting city with retry after invalid input"""
        city = self.cli_handler.collect_city()
        self.assertEqual(city, "Mumbai")
        output = mock_stdout.getvalue()
        self.assertIn("not found", output)
    
    @patch('builtins.input', side_effect=['', '', 'Mumbai'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_city_empty_input(self, mock_stdout, mock_input):
        """Test collecting city with empty input retry"""
        city = self.cli_handler.collect_city()
        self.assertEqual(city, "Mumbai")
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_collect_city_keyboard_interrupt(self, mock_input):
        """Test handling keyboard interrupt during city collection"""
        city = self.cli_handler.collect_city()
        self.assertIsNone(city)
    
    @patch('builtins.input', return_value='1')
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_price_range_valid_numeric(self, mock_stdout, mock_input):
        """Test collecting valid price range with numeric input"""
        price_range = self.cli_handler.collect_price_range()
        self.assertEqual(price_range, PriceRange.BUDGET)
        output = mock_stdout.getvalue()
        self.assertIn("Price range selected", output)
    
    @patch('builtins.input', return_value='Budget')
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_price_range_valid_text(self, mock_stdout, mock_input):
        """Test collecting valid price range with text input"""
        price_range = self.cli_handler.collect_price_range()
        self.assertEqual(price_range, PriceRange.BUDGET)
    
    @patch('builtins.input', side_effect=['invalid', '1'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_price_range_with_retry(self, mock_stdout, mock_input):
        """Test collecting price range with retry"""
        price_range = self.cli_handler.collect_price_range()
        self.assertEqual(price_range, PriceRange.BUDGET)
        output = mock_stdout.getvalue()
        self.assertIn("Invalid price range", output)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_collect_price_range_keyboard_interrupt(self, mock_input):
        """Test handling keyboard interrupt during price range collection"""
        price_range = self.cli_handler.collect_price_range()
        self.assertIsNone(price_range)
    
    @patch('builtins.input', side_effect=['Mumbai', '1', 'y'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_user_input_complete(self, mock_stdout, mock_input):
        """Test collecting complete user input"""
        result = self.cli_handler.collect_user_input()
        self.assertIsNotNone(result)
        self.assertEqual(result['city'], 'Mumbai')
        self.assertEqual(result['price_range'], PriceRange.BUDGET)
        output = mock_stdout.getvalue()
        self.assertIn("Selection Summary", output)
    
    @patch('builtins.input', side_effect=['Mumbai', '1', 'n'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_user_input_cancelled(self, mock_stdout, mock_input):
        """Test user cancelling input"""
        result = self.cli_handler.collect_user_input()
        self.assertIsNone(result)
        output = mock_stdout.getvalue()
        self.assertIn("cancelled", output)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_collect_user_input_keyboard_interrupt(self, mock_input):
        """Test handling keyboard interrupt during user input"""
        result = self.cli_handler.collect_user_input()
        self.assertIsNone(result)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_processing(self, mock_stdout):
        """Test displaying processing message"""
        self.cli_handler.display_processing()
        output = mock_stdout.getvalue()
        self.assertIn("Processing", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_error(self, mock_stdout):
        """Test displaying error message"""
        self.cli_handler.display_error("Test error message")
        output = mock_stdout.getvalue()
        self.assertIn("Error", output)
        self.assertIn("Test error message", output)
    
    @patch('builtins.input', return_value='y')
    def test_prompt_continue_yes(self, mock_input):
        """Test prompt continue with yes"""
        result = self.cli_handler.prompt_continue()
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='n')
    def test_prompt_continue_no(self, mock_input):
        """Test prompt continue with no"""
        result = self.cli_handler.prompt_continue()
        self.assertFalse(result)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_prompt_continue_interrupt(self, mock_input):
        """Test prompt continue with keyboard interrupt"""
        result = self.cli_handler.prompt_continue()
        self.assertFalse(result)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_goodbye(self, mock_stdout):
        """Test displaying goodbye message"""
        self.cli_handler.display_goodbye()
        output = mock_stdout.getvalue()
        self.assertIn("Thank you", output)


if __name__ == '__main__':
    unittest.main()
