"""
Limited test suite for Phase 4 - Minimizes Groq API calls
Tests critical functionality with edge cases
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from groq_client import GroqClient
from prompt_builder import PromptBuilder
from recommendation_engine import RecommendationEngine


class TestPhase4Limited(unittest.TestCase):
    """Limited test suite with minimal API calls"""
    
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
    
    def test_1_groq_client_initialization(self):
        """Test 1: Groq client initialization with environment variables"""
        # Test that client can be initialized (doesn't make API call)
        try:
            client = GroqClient()
            self.assertIsNotNone(client.api_key)
            self.assertIsNotNone(client.model)
            self.assertEqual(client.temperature, 0.3)
            print("[PASS] Test 1 passed: Groq client initialized successfully")
        except ValueError as e:
            self.fail(f"Groq client initialization failed: {e}")
    
    def test_2_prompt_builder_functionality(self):
        """Test 2: Prompt builder creates valid prompts (no API call)"""
        builder = PromptBuilder()
        
        # Test prompt building
        prompt = builder.build_recommendation_prompt(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Mid-Range",
            max_recommendations=5
        )
        
        # Validate prompt structure
        self.assertIsInstance(prompt, str)
        self.assertIn("Mumbai", prompt)
        self.assertIn("Mid-Range", prompt)
        self.assertIn("Restaurant A", prompt)
        self.assertIn("RESTAURANT DATA", prompt)
        self.assertIn("USER PREFERENCES", prompt)
        self.assertIn("TASK", prompt)
        self.assertIn("OUTPUT FORMAT", prompt)
        
        # Test validation
        self.assertTrue(builder.validate_restaurant_data(self.sample_restaurants))
        self.assertFalse(builder.validate_restaurant_data([]))
        
        print("[PASS] Test 2 passed: Prompt builder works correctly")
    
    @unittest.skip("Skipping to reduce API usage")
    def test_3_groq_api_connection(self):
        """Test 3: Test Groq API connection (1 API call)"""
        try:
            client = GroqClient()
            result = client.test_connection()
            self.assertTrue(result, "Groq API connection test failed")
            print("[PASS] Test 3 passed: Groq API connection successful")
        except Exception as e:
            self.fail(f"Groq API connection test failed: {e}")
    
    def test_4_recommendation_engine_end_to_end(self):
        """Test 4: End-to-end recommendation generation (1 API call)"""
        try:
            engine = RecommendationEngine()
            
            # Generate recommendations
            success, recommendations, error = engine.generate_recommendations(
                restaurants=self.sample_restaurants,
                city="Mumbai",
                price_range="Mid-Range",
                max_recommendations=3  # Limit to reduce API usage
            )
            
            # Validate results
            self.assertTrue(success, f"Recommendation generation failed: {error}")
            self.assertIsNotNone(recommendations)
            self.assertGreater(len(recommendations), 0)
            self.assertLessEqual(len(recommendations), 3)
            
            # Validate structure
            first_rec = recommendations[0]
            required_fields = ['rank', 'restaurant_name', 'cuisine', 'rating', 'reasoning']
            for field in required_fields:
                self.assertIn(field, first_rec, f"Missing field: {field}")
            
            # Check history
            history = engine.get_recommendation_history()
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]['city'], "Mumbai")
            
            print(f"[PASS] Test 4 passed: Generated {len(recommendations)} recommendations successfully")
            print(f"  Sample recommendation: {recommendations[0]['restaurant_name']}")
            
        except Exception as e:
            self.fail(f"End-to-end test failed: {e}")
    
    def test_edge_case_empty_restaurants(self):
        """Edge Case 1: Empty restaurant list"""
        engine = RecommendationEngine()
        success, recommendations, error = engine.generate_recommendations(
            restaurants=[],
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        self.assertFalse(success)
        self.assertIsNone(recommendations)
        self.assertIsNotNone(error)
        print("[PASS] Edge case 1 passed: Empty restaurants handled correctly")
    
    def test_edge_case_invalid_restaurant_data(self):
        """Edge Case 2: Invalid restaurant data structure"""
        invalid_data = [
            {'name': 'Restaurant A'}  # Missing required fields
        ]
        
        engine = RecommendationEngine()
        success, recommendations, error = engine.generate_recommendations(
            restaurants=invalid_data,
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        self.assertFalse(success)
        self.assertIsNone(recommendations)
        self.assertIsNotNone(error)
        print("[PASS] Edge case 2 passed: Invalid data structure handled correctly")
    
    def test_edge_case_fallback_ranking(self):
        """Edge Case 3: Fallback ranking when LLM response is invalid"""
        # This test doesn't make an API call, just tests fallback logic
        builder = PromptBuilder()
        
        # Test fallback prompt
        fallback_prompt = builder.build_fallback_prompt(
            restaurants=self.sample_restaurants,
            city="Mumbai",
            price_range="Mid-Range"
        )
        
        self.assertIsInstance(fallback_prompt, str)
        self.assertIn("Mumbai", fallback_prompt)
        self.assertIn("Restaurant", fallback_prompt)
        print("[PASS] Edge case 3 passed: Fallback prompt generation works")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  PHASE 4 LIMITED TEST SUITE")
    print("  (Minimizes Groq API calls)")
    print("=" * 60 + "\n")
    
    unittest.main(verbosity=2)
