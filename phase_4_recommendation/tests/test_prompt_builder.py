"""
Test cases for Prompt Builder Module
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_builder import PromptBuilder


class TestPromptBuilder(unittest.TestCase):
    """Test cases for PromptBuilder"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.prompt_builder = PromptBuilder()
        self.sample_restaurants = [
            {
                'name': 'Restaurant A',
                'cuisine': 'Italian',
                'rating': 4.5,
                'review_count': 100,
                'price_range': 'Mid-Range',
                'key_features': 'Highly Rated, Popular',
                'composite_score': 0.85
            },
            {
                'name': 'Restaurant B',
                'cuisine': 'Chinese',
                'rating': 4.2,
                'review_count': 80,
                'price_range': 'Budget',
                'key_features': 'Well Rated',
                'composite_score': 0.75
            }
        ]
    
    def test_initialization(self):
        """Test prompt builder initialization"""
        self.assertIsNotNone(self.prompt_builder)
        self.assertIsNotNone(self.prompt_builder.system_role)
    
    def test_build_recommendation_prompt(self):
        """Test building recommendation prompt"""
        prompt = self.prompt_builder.build_recommendation_prompt(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Mid-Range",
            max_recommendations=5
        )
        
        self.assertIsInstance(prompt, str)
        self.assertIn("Mumbai", prompt)
        self.assertIn("Mid-Range", prompt)
        self.assertIn("Restaurant A", prompt)
        self.assertIn("Restaurant B", prompt)
    
    def test_build_restaurant_context(self):
        """Test building restaurant context"""
        context = self.prompt_builder._build_restaurant_context(self.sample_restaurants)
        
        self.assertIn("RESTAURANT DATA", context)
        self.assertIn("Restaurant A", context)
        self.assertIn("Italian", context)
        self.assertIn("4.5", context)
    
    def test_build_user_preferences(self):
        """Test building user preferences section"""
        preferences = self.prompt_builder._build_user_preferences("Delhi", "Premium")
        
        self.assertIn("Delhi", preferences)
        self.assertIn("Premium", preferences)
        self.assertIn("USER PREFERENCES", preferences)
    
    def test_build_task_definition(self):
        """Test building task definition"""
        task = self.prompt_builder._build_task_definition(10)
        
        self.assertIn("10", task)
        self.assertIn("TASK", task)
        self.assertIn("recommend", task.lower())
    
    def test_build_output_format(self):
        """Test building output format"""
        output_format = self.prompt_builder._build_output_format()
        
        self.assertIn("OUTPUT FORMAT", output_format)
        self.assertIn("JSON", output_format)
        self.assertIn("rank", output_format)
        self.assertIn("restaurant_name", output_format)
    
    def test_get_system_prompt(self):
        """Test getting system prompt"""
        system_prompt = self.prompt_builder.get_system_prompt()
        
        self.assertIsInstance(system_prompt, str)
        self.assertIn("expert", system_prompt.lower())
        self.assertIn("restaurant", system_prompt.lower())
    
    def test_build_fallback_prompt(self):
        """Test building fallback prompt"""
        fallback = self.prompt_builder.build_fallback_prompt(
            restaurants=self.sample_restaurants,
            city="Bangalore",
            price_range="Budget"
        )
        
        self.assertIn("Bangalore", fallback)
        self.assertIn("Budget", fallback)
        self.assertIn("Restaurant A", fallback)
    
    def test_validate_restaurant_data_valid(self):
        """Test validation of valid restaurant data"""
        result = self.prompt_builder.validate_restaurant_data(self.sample_restaurants)
        self.assertTrue(result)
    
    def test_validate_restaurant_data_invalid(self):
        """Test validation of invalid restaurant data"""
        invalid_data = [
            {'name': 'Restaurant A'}  # Missing required fields
        ]
        
        result = self.prompt_builder.validate_restaurant_data(invalid_data)
        self.assertFalse(result)
    
    def test_validate_restaurant_data_empty(self):
        """Test validation of empty restaurant data"""
        result = self.prompt_builder.validate_restaurant_data([])
        self.assertFalse(result)
    
    def test_prompt_includes_all_sections(self):
        """Test that prompt includes all required sections"""
        prompt = self.prompt_builder.build_recommendation_prompt(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        # Check for key sections
        self.assertIn("RESTAURANT DATA", prompt)
        self.assertIn("USER PREFERENCES", prompt)
        self.assertIn("TASK", prompt)
        self.assertIn("OUTPUT FORMAT", prompt)


if __name__ == '__main__':
    unittest.main()
