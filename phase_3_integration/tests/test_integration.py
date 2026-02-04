"""
Integration tests for Phase 3 components
Tests interaction between filter manager, enrichment engine, and orchestration service
"""

import unittest
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filter_manager import FilterManager, PriceRange
from enrichment_engine import EnrichmentEngine
from orchestration_service import OrchestrationService


class TestPhase3Integration(unittest.TestCase):
    """Integration tests for Phase 3"""
    
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
    
    def test_filter_to_enrichment_flow(self):
        """Test flow from filtering to enrichment"""
        # Step 1: Filter
        filter_manager = FilterManager(self.sample_data)
        filtered = filter_manager.filter_restaurants("Mumbai", PriceRange.MID_RANGE)
        
        self.assertGreater(len(filtered), 0)
        
        # Step 2: Enrich
        enrichment_engine = EnrichmentEngine(filtered)
        enriched = enrichment_engine.enrich()
        
        self.assertIsNotNone(enriched)
        self.assertGreater(len(enriched), 0)
        self.assertIn('enriched_composite_score', enriched.columns)
        
        # Step 3: Prepare for LLM
        llm_data = enrichment_engine.prepare_for_llm()
        
        self.assertIsInstance(llm_data, list)
        self.assertGreater(len(llm_data), 0)
    
    def test_orchestration_complete_flow(self):
        """Test complete orchestration flow"""
        orchestration = OrchestrationService(self.sample_data)
        
        success, llm_data, error = orchestration.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE,
            min_rating=3.5,
            min_reviews=30,
            max_candidates=5
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(llm_data)
        self.assertIsNone(error)
        
        # Verify components were created
        self.assertIsNotNone(orchestration.filter_manager)
        self.assertIsNotNone(orchestration.enrichment_engine)
        
        # Verify data flow
        filtered = orchestration.get_filtered_candidates()
        enriched = orchestration.get_enriched_data()
        
        self.assertIsNotNone(filtered)
        self.assertIsNotNone(enriched)
        self.assertLessEqual(len(llm_data), len(enriched))
    
    def test_multiple_cities_processing(self):
        """Test processing requests for multiple cities"""
        orchestration = OrchestrationService(self.sample_data)
        
        cities = ["Mumbai", "Delhi", "Bangalore"]
        results = {}
        
        for city in cities:
            success, llm_data, error = orchestration.process_user_request(
                city=city,
                price_range=PriceRange.MID_RANGE,
                max_candidates=3
            )
            results[city] = {
                'success': success,
                'count': len(llm_data) if llm_data else 0
            }
            orchestration.reset()
        
        # Verify all cities processed
        self.assertEqual(len(results), 3)
        for city, result in results.items():
            self.assertIn('success', result)
            self.assertIn('count', result)
    
    def test_different_price_ranges(self):
        """Test processing with different price ranges"""
        orchestration = OrchestrationService(self.sample_data)
        
        price_ranges = [PriceRange.BUDGET, PriceRange.MID_RANGE, PriceRange.PREMIUM]
        results = {}
        
        for price_range in price_ranges:
            success, llm_data, error = orchestration.process_user_request(
                city="Mumbai",
                price_range=price_range,
                max_candidates=3
            )
            results[price_range.value] = {
                'success': success,
                'count': len(llm_data) if llm_data else 0
            }
            orchestration.reset()
        
        # Verify all price ranges processed
        self.assertEqual(len(results), 3)
    
    def test_data_consistency(self):
        """Test data consistency through pipeline"""
        orchestration = OrchestrationService(self.sample_data)
        
        success, llm_data, error = orchestration.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        if success and llm_data:
            # Verify all LLM data items have required fields
            for item in llm_data:
                self.assertIn('restaurant_id', item)
                self.assertIn('name', item)
                self.assertIn('city', item)
                self.assertEqual(item['city'], 'Mumbai')
                self.assertIn('price_range', item)
                self.assertEqual(item['price_range'], 'Mid-Range')
    
    def test_statistics_accuracy(self):
        """Test that statistics are accurate"""
        orchestration = OrchestrationService(self.sample_data)
        
        initial_count = len(self.sample_data)
        
        success, llm_data, error = orchestration.process_user_request(
            city="Mumbai",
            price_range=PriceRange.MID_RANGE
        )
        
        stats = orchestration.get_processing_stats()
        
        self.assertEqual(stats['initial_count'], initial_count)
        self.assertIn('filter_stats', stats)
        self.assertIn('enrichment_stats', stats)
        
        if stats['filter_stats']:
            self.assertLessEqual(stats['filter_stats']['final_count'], initial_count)


if __name__ == '__main__':
    unittest.main()
