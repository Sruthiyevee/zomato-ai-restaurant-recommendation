"""
Filter Manager Module for Phase 3
Handles geographic and price-based filtering of restaurants
"""

import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceRange(Enum):
    """Price range categories"""
    BUDGET = "Budget"
    MID_RANGE = "Mid-Range"
    PREMIUM = "Premium"
    LUXURY = "Luxury"


class FilterManager:
    """Manages filtering operations for restaurants"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize filter manager
        
        Args:
            data: DataFrame containing restaurant data
        """
        self.data = data.copy()
        self.filtered_data = None
        self.filter_stats = {}
        
    def apply_geographic_filter(self, city: str) -> pd.DataFrame:
        """
        Apply geographic filter by city
        
        Args:
            city: City name to filter by
            
        Returns:
            Filtered DataFrame
        """
        logger.info(f"Applying geographic filter for city: {city}")
        
        if self.data.empty:
            logger.warning("No data available for filtering")
            return pd.DataFrame()
        
        # Find city column (case-insensitive)
        city_col = None
        for col in self.data.columns:
            if col.lower() == 'city':
                city_col = col
                break
        
        if not city_col:
            logger.error("City column not found in data")
            return pd.DataFrame()
        
        # Filter by city (case-insensitive)
        city_normalized = city.strip().title()
        filtered = self.data[
            self.data[city_col].astype(str).str.strip().str.title() == city_normalized
        ].copy()
        
        logger.info(f"Geographic filter: {len(self.data)} -> {len(filtered)} restaurants")
        
        return filtered
    
    def apply_price_filter(self, price_range: PriceRange, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Apply price range filter
        
        Args:
            price_range: PriceRange enum value
            data: Optional DataFrame to filter (uses self.data if not provided)
            
        Returns:
            Filtered DataFrame
        """
        logger.info(f"Applying price filter for: {price_range.value}")
        
        source_data = data if data is not None else self.data
        
        if source_data.empty:
            logger.warning("No data available for price filtering")
            return pd.DataFrame()
        
        # Find price range column
        price_col = None
        for col in source_data.columns:
            if 'price' in col.lower() and 'range' in col.lower():
                price_col = col
                break
        
        if not price_col:
            logger.warning("Price range column not found, skipping price filter")
            return source_data
        
        # Filter by price range
        filtered = source_data[
            source_data[price_col].astype(str).str.strip() == price_range.value
        ].copy()
        
        logger.info(f"Price filter: {len(source_data)} -> {len(filtered)} restaurants")
        
        return filtered
    
    def apply_quality_filter(
        self,
        data: Optional[pd.DataFrame] = None,
        min_rating: float = 3.0,
        min_reviews: int = 10
    ) -> pd.DataFrame:
        """
        Apply quality filters (minimum rating and review count)
        
        Args:
            data: Optional DataFrame to filter
            min_rating: Minimum rating threshold (default: 3.0)
            min_reviews: Minimum review count threshold (default: 10)
            
        Returns:
            Filtered DataFrame
        """
        logger.info(f"Applying quality filter: min_rating={min_rating}, min_reviews={min_reviews}")
        
        source_data = data if data is not None else self.data
        
        if source_data.empty:
            return pd.DataFrame()
        
        filtered = source_data.copy()
        
        # Filter by minimum rating
        rating_col = None
        for col in filtered.columns:
            if 'rating' in col.lower() and 'normalized' in col.lower():
                rating_col = col
                break
            elif 'rating' in col.lower():
                rating_col = col
        
        if rating_col:
            filtered = filtered[filtered[rating_col] >= min_rating]
            logger.info(f"Rating filter: {len(source_data)} -> {len(filtered)} restaurants")
        
        # Filter by minimum review count
        review_count_col = None
        for col in filtered.columns:
            if 'review' in col.lower() and 'count' in col.lower():
                review_count_col = col
                break
        
        if review_count_col:
            filtered = filtered[filtered[review_count_col] >= min_reviews]
            logger.info(f"Review count filter: {len(filtered)} restaurants")
        
        return filtered
    
    def filter_restaurants(
        self,
        city: str,
        price_range: PriceRange,
        min_rating: float = 3.0,
        min_reviews: int = 10
    ) -> pd.DataFrame:
        """
        Apply all filters in sequence
        
        Args:
            city: City name
            price_range: PriceRange enum
            min_rating: Minimum rating threshold
            min_reviews: Minimum review count threshold
            
        Returns:
            Filtered DataFrame
        """
        logger.info("Starting multi-stage filtering pipeline")
        
        initial_count = len(self.data)
        
        # Stage 1: Geographic filter
        filtered = self.apply_geographic_filter(city)
        if filtered.empty:
            logger.warning("No restaurants found after geographic filter")
            self.filtered_data = filtered
            self._update_filter_stats(initial_count, 0)
            return filtered
        
        # Stage 2: Price range filter
        filtered = self.apply_price_filter(price_range, filtered)
        if filtered.empty:
            logger.warning("No restaurants found after price filter")
            self.filtered_data = filtered
            self._update_filter_stats(initial_count, 0)
            return filtered
        
        # Stage 3: Quality filter
        filtered = self.apply_quality_filter(filtered, min_rating, min_reviews)
        
        self.filtered_data = filtered
        self._update_filter_stats(initial_count, len(filtered))
        
        logger.info(f"Filtering complete: {initial_count} -> {len(filtered)} restaurants")
        
        return filtered
    
    def optimize_candidates(
        self,
        data: Optional[pd.DataFrame] = None,
        max_candidates: int = 50,
        ensure_diversity: bool = True
    ) -> pd.DataFrame:
        """
        Optimize candidate set by ranking and ensuring diversity
        
        Args:
            data: Optional DataFrame to optimize
            max_candidates: Maximum number of candidates to return
            ensure_diversity: Whether to ensure cuisine diversity
            
        Returns:
            Optimized DataFrame
        """
        logger.info(f"Optimizing candidates (max: {max_candidates})")
        
        source_data = data if data is not None else (self.filtered_data if self.filtered_data is not None else self.data)
        
        if source_data.empty:
            return pd.DataFrame()
        
        # Rank by composite score if available
        composite_col = None
        for col in source_data.columns:
            if 'composite' in col.lower() and 'score' in col.lower():
                composite_col = col
                break
        
        if composite_col:
            # Sort by composite score (descending)
            optimized = source_data.sort_values(by=composite_col, ascending=False)
        else:
            # Fallback: sort by rating
            rating_col = None
            for col in source_data.columns:
                if 'rating' in col.lower():
                    rating_col = col
                    break
            
            if rating_col:
                optimized = source_data.sort_values(by=rating_col, ascending=False)
            else:
                optimized = source_data
        
        # Ensure diversity if requested
        if ensure_diversity and len(optimized) > max_candidates:
            optimized = self._ensure_diversity(optimized, max_candidates)
        else:
            optimized = optimized.head(max_candidates)
        
        logger.info(f"Candidate optimization: {len(source_data)} -> {len(optimized)} restaurants")
        
        return optimized
    
    def _ensure_diversity(self, data: pd.DataFrame, max_count: int) -> pd.DataFrame:
        """
        Ensure diversity in candidate set (cuisine variety)
        
        Args:
            data: DataFrame to diversify
            max_count: Maximum number of candidates
            
        Returns:
            Diversified DataFrame
        """
        # Find cuisine column
        cuisine_col = None
        for col in data.columns:
            if 'cuisine' in col.lower() and 'primary' in col.lower():
                cuisine_col = col
                break
        
        if not cuisine_col or cuisine_col not in data.columns:
            # No cuisine info, just return top N
            return data.head(max_count)
        
        # Group by cuisine and take top restaurants from each
        diversified = []
        cuisines = data[cuisine_col].unique()
        per_cuisine = max(1, max_count // len(cuisines)) if len(cuisines) > 0 else max_count
        
        for cuisine in cuisines:
            cuisine_data = data[data[cuisine_col] == cuisine].head(per_cuisine)
            diversified.append(cuisine_data)
        
        result = pd.concat(diversified, ignore_index=True)
        
        # If we have fewer than max_count, fill with remaining top restaurants
        if len(result) < max_count:
            remaining = max_count - len(result)
            remaining_data = data[~data.index.isin(result.index)].head(remaining)
            result = pd.concat([result, remaining_data], ignore_index=True)
        
        return result.head(max_count)
    
    def _update_filter_stats(self, initial_count: int, final_count: int) -> None:
        """Update filtering statistics"""
        self.filter_stats = {
            'initial_count': initial_count,
            'final_count': final_count,
            'filtered_out': initial_count - final_count,
            'retention_rate': (final_count / initial_count * 100) if initial_count > 0 else 0
        }
    
    def get_filter_stats(self) -> Dict:
        """Get filtering statistics"""
        return self.filter_stats.copy()
    
    def get_filtered_data(self) -> Optional[pd.DataFrame]:
        """Get filtered data"""
        return self.filtered_data
