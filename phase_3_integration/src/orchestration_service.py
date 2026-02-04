"""
Orchestration Service Module for Phase 3
Coordinates filtering, enrichment, and data flow between components
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd

from filter_manager import FilterManager, PriceRange
from enrichment_engine import EnrichmentEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestrationService:
    """Orchestrates data flow between filtering and enrichment components"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize orchestration service
        
        Args:
            data: DataFrame containing restaurant data
        """
        self.data = data
        self.filter_manager = None
        self.enrichment_engine = None
        self.processed_data = None
        self.execution_log = []
        
    def process_user_request(
        self,
        city: str,
        price_range: PriceRange,
        min_rating: float = 3.0,
        min_reviews: int = 10,
        max_candidates: int = 50
    ) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Process complete user request through filtering and enrichment pipeline
        
        Args:
            city: City name
            price_range: PriceRange enum
            min_rating: Minimum rating threshold
            min_reviews: Minimum review count threshold
            max_candidates: Maximum number of candidates for LLM
            
        Returns:
            Tuple of (success, llm_data, error_message)
        """
        try:
            logger.info(f"Processing request: city={city}, price_range={price_range.value}")
            self._log("Starting request processing")
            
            # Step 1: Initialize components
            self._log("Initializing filter manager and enrichment engine")
            self.filter_manager = FilterManager(self.data)
            self.enrichment_engine = None  # Will be initialized after filtering
            
            # Step 2: Apply filters
            self._log("Applying filters")
            filtered_data = self.filter_manager.filter_restaurants(
                city=city,
                price_range=price_range,
                min_rating=min_rating,
                min_reviews=min_reviews
            )
            
            if filtered_data.empty:
                error_msg = f"No restaurants found matching criteria: {city}, {price_range.value}"
                self._log(f"Error: {error_msg}")
                return False, None, error_msg
            
            # Step 3: Optimize candidates
            self._log("Optimizing candidate set")
            optimized_data = self.filter_manager.optimize_candidates(
                data=filtered_data,
                max_candidates=max_candidates,
                ensure_diversity=True
            )
            
            if optimized_data.empty:
                error_msg = "No restaurants available after optimization"
                self._log(f"Error: {error_msg}")
                return False, None, error_msg
            
            # Step 4: Enrich data
            self._log("Enriching restaurant data")
            self.enrichment_engine = EnrichmentEngine(optimized_data)
            enriched_data = self.enrichment_engine.enrich()
            
            if enriched_data.empty:
                error_msg = "Data enrichment failed"
                self._log(f"Error: {error_msg}")
                return False, None, error_msg
            
            # Step 5: Prepare for LLM
            self._log("Preparing data for LLM")
            llm_data = self.enrichment_engine.prepare_for_llm(max_restaurants=max_candidates)
            
            if not llm_data:
                error_msg = "Failed to prepare data for LLM"
                self._log(f"Error: {error_msg}")
                return False, None, error_msg
            
            self.processed_data = enriched_data
            self._log("Request processing completed successfully")
            
            return True, llm_data, None
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._log(f"Error: {error_msg}")
            return False, None, error_msg
    
    def get_filtered_candidates(self) -> Optional[pd.DataFrame]:
        """
        Get filtered candidate restaurants (before enrichment)
        
        Returns:
            DataFrame with filtered candidates
        """
        if self.filter_manager:
            return self.filter_manager.get_filtered_data()
        return None
    
    def get_enriched_data(self) -> Optional[pd.DataFrame]:
        """
        Get enriched restaurant data
        
        Returns:
            DataFrame with enriched data
        """
        if self.enrichment_engine:
            return self.enrichment_engine.get_enriched_data()
        return self.processed_data
    
    def get_processing_stats(self) -> Dict:
        """
        Get processing statistics
        
        Returns:
            Dictionary with processing statistics
        """
        stats = {
            'initial_count': len(self.data),
            'filter_stats': {},
            'enrichment_stats': {},
            'final_candidate_count': 0,
            'execution_log': self.execution_log.copy()
        }
        
        if self.filter_manager:
            stats['filter_stats'] = self.filter_manager.get_filter_stats()
            filtered_data = self.filter_manager.get_filtered_data()
            if filtered_data is not None:
                stats['final_candidate_count'] = len(filtered_data)
        
        if self.enrichment_engine:
            stats['enrichment_stats'] = self.enrichment_engine.get_enrichment_stats()
        
        return stats
    
    def _log(self, message: str) -> None:
        """Log execution step"""
        logger.info(message)
        self.execution_log.append(message)
    
    def reset(self) -> None:
        """Reset orchestration service state"""
        self.filter_manager = None
        self.enrichment_engine = None
        self.processed_data = None
        self.execution_log = []
        logger.info("Orchestration service reset")
