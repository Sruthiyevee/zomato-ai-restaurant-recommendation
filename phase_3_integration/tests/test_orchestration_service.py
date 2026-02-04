"""
Test cases for Orchestration Service Module
"""

import unittest
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestration_service import OrchestrationService
from filter_manager import PriceRange


class TestOrchestrationService(unittest.TestCase):
    """Test cases for OrchestrationService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_data = pd.DataFrame({
            'restaurant_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'restaurant_name': ['Restaurant A', 'Restaurant B', 'Restaurant C', 'Restaurant D', 'Restaurant E',
                               'Restaurant F', 'Restaurant G', 'Restaurant H', 'Restaurant I', 'Restaurant J'],
            'city': ['Mumbai', 'Mumbai', 'Delhi', 'Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Delhi', 'Mumbai', 'Bangalore'],
            'price_range': ['Budget', 'Mid-Range', 'Premium', 'Budget', 'Mid-Range', 'Premium', 'Luxury', 'Budget', 'Mid-Range', 'Premium'],
            'normalized_rating': [4.5, 3.8, 4.2, 4.0, 3.5, 4.8, 3.2, 4.3, 3.9, 4.1],
            'review_count': [100, 50, 200, 75, 30, 150, 25, 120, 60, 180],
            'primary_cuisine': ['Italian', 'Chinese', 'Indian', 'Italian', 'Chinese', 'Indian', 'Italian', 'Indian', 'Chinese', 'Italian'],
            'composite_score': [0.8, 0.6, 0.9, 0.7, 0.5, 0.95, 0.4, 0.85, 0.65, 0.75],
            'popularity_score': [0.8, 0.6, 0.9, 0.7, 0.5, 0.95, 0.4, 0.85, 0.65, 0.75]
        })
        self.orchestration_service = OrchestrationService(self.sample_data)
    
    def test_initialization(self):
        """Test orchestration service initialization"""
        self.assertIsNotNone(self.orchestration_service)
        self.assertIsNotNone(self.orchestration_service.data)
        self.assertIsNone(self.orchestration_service.filter_manager)
        self.assertIsNone(self.orchestration_service.enrichment_engine)
        self.assertEqual(len(self.orchestration_service.execution_log), 0)
    
    def test_process_user_request_success(self):
        """Test successful request processing"""
        success, llm_data, error = self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE,
            min_rating=3.5,
            min_reviews=30,
            max_candidates=5
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(llm_data)
        self.assertIsInstance(llm_data, list)
        self.assertIsNone(error)
        self.assertGreater(len(llm_data), 0)
    
    def test_process_user_request_no_results(self):
        """Test request processing with no matching results"""
        success, llm_data, error = self.orchestration_service.process_user_request(
            city="Pune",
            price_range=PriceRange.LUXURY,
            min_rating=5.0,
            min_reviews=1000
        )
        
        self.assertFalse(success)
        self.assertIsNone(llm_data)
        self.assertIsNotNone(error)
    
    def test_process_user_request_creates_components(self):
        """Test that processing creates filter manager and enrichment engine"""
        self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        self.assertIsNotNone(self.orchestration_service.filter_manager)
        self.assertIsNotNone(self.orchestration_service.enrichment_engine)
    
    def test_get_filtered_candidates(self):
        """Test getting filtered candidates"""
        self.assertIsNone(self.orchestration_service.get_filtered_candidates())
        
        self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        candidates = self.orchestration_service.get_filtered_candidates()
        self.assertIsNotNone(candidates)
        self.assertIsInstance(candidates, pd.DataFrame)
    
    def test_get_enriched_data(self):
        """Test getting enriched data"""
        self.assertIsNone(self.orchestration_service.get_enriched_data())
        
        self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        enriched = self.orchestration_service.get_enriched_data()
        self.assertIsNotNone(enriched)
        self.assertIsInstance(enriched, pd.DataFrame)
    
    def test_get_processing_stats(self):
        """Test getting processing statistics"""
        stats = self.orchestration_service.get_processing_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('initial_count', stats)
        self.assertIn('filter_stats', stats)
        self.assertIn('enrichment_stats', stats)
        self.assertIn('execution_log', stats)
        
        # After processing
        self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        stats = self.orchestration_service.get_processing_stats()
        self.assertGreater(len(stats['execution_log']), 0)
        self.assertIn('filter_stats', stats)
    
    def test_execution_log(self):
        """Test execution logging"""
        initial_log_length = len(self.orchestration_service.execution_log)
        
        self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        self.assertGreater(len(self.orchestration_service.execution_log), initial_log_length)
        self.assertIn('Starting request processing', self.orchestration_service.execution_log[0])
    
    def test_reset(self):
        """Test resetting orchestration service"""
        self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        self.assertIsNotNone(self.orchestration_service.filter_manager)
        self.assertGreater(len(self.orchestration_service.execution_log), 0)
        
        self.orchestration_service.reset()
        
        self.assertIsNone(self.orchestration_service.filter_manager)
        self.assertIsNone(self.orchestration_service.enrichment_engine)
        self.assertEqual(len(self.orchestration_service.execution_log), 0)
    
    def test_llm_data_structure(self):
        """Test LLM data structure"""
        success, llm_data, error = self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE,
            max_candidates=3
        )
        
        if success and llm_data:
            first_item = llm_data[0]
            required_fields = ['restaurant_id', 'name', 'city', 'cuisine', 'rating', 
                             'review_count', 'price_range', 'key_features', 'composite_score']
            
            for field in required_fields:
                self.assertIn(field, first_item, f"Missing field: {field}")
    
    def test_max_candidates_limit(self):
        """Test that max_candidates limit is respected"""
        success, llm_data, error = self.orchestration_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE,
            max_candidates=2
        )
        
        if success:
            self.assertLessEqual(len(llm_data), 2)
    
    def test_empty_data(self):
        """Test handling of empty data"""
        empty_service = OrchestrationService(pd.DataFrame())
        success, llm_data, error = empty_service.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        self.assertFalse(success)
        self.assertIsNone(llm_data)
        self.assertIsNotNone(error)


if __name__ == '__main__':
    unittest.main()
