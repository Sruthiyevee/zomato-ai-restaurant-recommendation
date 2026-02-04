"""
Test cases for Recommendation Engine Module
"""

import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from recommendation_engine import RecommendationEngine
from groq_client import GroqClient
from prompt_builder import PromptBuilder


class TestRecommendationEngine(unittest.TestCase):
    """Test cases for RecommendationEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
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
            },
            {
                'name': 'Restaurant C',
                'cuisine': 'Indian',
                'rating': 4.8,
                'review_count': 150,
                'price_range': 'Premium',
                'key_features': 'Highly Rated, Very Popular',
                'composite_score': 0.95
            }
        ]
    
    @patch('groq_client.GroqClient')
    def test_initialization(self, mock_groq_class):
        """Test recommendation engine initialization"""
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        engine = RecommendationEngine()
        
        self.assertIsNotNone(engine)
        self.assertIsNotNone(engine.groq_client)
        self.assertIsNotNone(engine.prompt_builder)
        self.assertEqual(len(engine.recommendation_history), 0)
    
    @patch('groq_client.GroqClient')
    def test_generate_recommendations_success(self, mock_groq_class):
        """Test successful recommendation generation"""
        mock_client = MagicMock()
        mock_client.generate_recommendations.return_value = '''[
            {
                "rank": 1,
                "restaurant_name": "Restaurant C",
                "cuisine": "Indian",
                "rating": 4.8,
                "price_range": "Premium",
                "reasoning": "Highest rating and excellent reviews",
                "key_highlights": "Highly Rated, Very Popular"
            }
        ]'''
        mock_groq_class.return_value = mock_client
        
        engine = RecommendationEngine(groq_client=mock_client)
        success, recommendations, error = engine.generate_recommendations(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Premium",
            max_recommendations=5
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(recommendations)
        self.assertIsNone(error)
        self.assertGreater(len(recommendations), 0)
    
    @patch('groq_client.GroqClient')
    def test_generate_recommendations_empty_input(self, mock_groq_class):
        """Test recommendation generation with empty input"""
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        engine = RecommendationEngine(groq_client=mock_client)
        success, recommendations, error = engine.generate_recommendations(
            restaurants=[],
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        self.assertFalse(success)
        self.assertIsNone(recommendations)
        self.assertIsNotNone(error)
    
    @patch('groq_client.GroqClient')
    def test_generate_recommendations_fallback(self, mock_groq_class):
        """Test fallback ranking when LLM response is invalid"""
        mock_client = MagicMock()
        mock_client.generate_recommendations.return_value = "Invalid response format"
        mock_groq_class.return_value = mock_client
        
        engine = RecommendationEngine(groq_client=mock_client)
        success, recommendations, error = engine.generate_recommendations(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        # Should use fallback ranking
        self.assertTrue(success)
        self.assertIsNotNone(recommendations)
        self.assertGreater(len(recommendations), 0)
    
    @patch('groq_client.GroqClient')
    def test_validate_recommendations(self, mock_groq_class):
        """Test recommendation validation"""
        mock_client = MagicMock()
        mock_client.generate_recommendations.return_value = '''[
            {
                "rank": 1,
                "restaurant_name": "Restaurant A",
                "cuisine": "Italian",
                "rating": 4.5,
                "price_range": "Mid-Range",
                "reasoning": "Great restaurant",
                "key_highlights": "Highly Rated"
            }
        ]'''
        mock_groq_class.return_value = mock_client
        
        engine = RecommendationEngine(groq_client=mock_client)
        success, recommendations, error = engine.generate_recommendations(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        if success and recommendations:
            # Check structure
            first_rec = recommendations[0]
            self.assertIn('rank', first_rec)
            self.assertIn('restaurant_name', first_rec)
            self.assertIn('cuisine', first_rec)
            self.assertIn('rating', first_rec)
            self.assertIn('reasoning', first_rec)
    
    @patch('groq_client.GroqClient')
    def test_recommendation_history(self, mock_groq_class):
        """Test recommendation history tracking"""
        mock_client = MagicMock()
        mock_client.generate_recommendations.return_value = '''[
            {
                "rank": 1,
                "restaurant_name": "Restaurant A",
                "cuisine": "Italian",
                "rating": 4.5,
                "price_range": "Mid-Range",
                "reasoning": "Test",
                "key_highlights": "Test"
            }
        ]'''
        mock_groq_class.return_value = mock_client
        
        engine = RecommendationEngine(groq_client=mock_client)
        engine.generate_recommendations(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        history = engine.get_recommendation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['city'], "Mumbai")
        self.assertEqual(history[0]['price_range'], "Mid-Range")
    
    @patch('groq_client.GroqClient')
    def test_test_groq_connection(self, mock_groq_class):
        """Test Groq connection testing"""
        mock_client = MagicMock()
        mock_client.test_connection.return_value = True
        mock_groq_class.return_value = mock_client
        
        engine = RecommendationEngine(groq_client=mock_client)
        result = engine.test_groq_connection()
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
