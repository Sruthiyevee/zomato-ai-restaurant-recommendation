"""
Enrichment Engine Module for Phase 3
Handles feature aggregation and data enrichment for restaurants
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnrichmentEngine:
    """Enriches restaurant data with aggregated features"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize enrichment engine
        
        Args:
            data: DataFrame containing restaurant data
        """
        self.data = data.copy()
        self.enriched_data = None
        
    def enrich(self) -> pd.DataFrame:
        """
        Perform comprehensive data enrichment
        
        Returns:
            Enriched DataFrame
        """
        logger.info("Starting data enrichment")
        
        if self.data.empty:
            logger.warning("No data to enrich")
            return pd.DataFrame()
        
        self.enriched_data = self.data.copy()
        
        # Aggregate review data
        self._aggregate_reviews()
        
        # Calculate composite scores
        self._calculate_composite_scores()
        
        # Extract key features
        self._extract_key_features()
        
        logger.info(f"Enrichment complete: {len(self.enriched_data)} restaurants enriched")
        
        return self.enriched_data
    
    def _aggregate_reviews(self) -> None:
        """Aggregate review-related metrics"""
        logger.info("Aggregating review data")
        
        # Ensure review_count exists
        if 'review_count' not in self.enriched_data.columns:
            review_count_col = None
            for col in self.enriched_data.columns:
                if 'review' in col.lower() and 'count' in col.lower():
                    review_count_col = col
                    break
            
            if review_count_col:
                self.enriched_data['review_count'] = pd.to_numeric(
                    self.enriched_data[review_count_col], errors='coerce'
                ).fillna(0).astype(int)
            else:
                self.enriched_data['review_count'] = 0
        
        # Calculate review statistics
        if 'review_count' in self.enriched_data.columns:
            self.enriched_data['has_reviews'] = self.enriched_data['review_count'] > 0
            self.enriched_data['review_count_category'] = pd.cut(
                self.enriched_data['review_count'],
                bins=[0, 10, 50, 200, np.inf],
                labels=['Low', 'Medium', 'High', 'Very High'],
                include_lowest=True
            )
    
    def _calculate_composite_scores(self) -> None:
        """Calculate composite quality scores"""
        logger.info("Calculating composite scores")
        
        # Get rating column
        rating_col = None
        for col in self.enriched_data.columns:
            if 'normalized_rating' in col.lower() or ('rating' in col.lower() and 'normalized' in col.lower()):
                rating_col = col
                break
            elif 'rating' in col.lower():
                rating_col = col
        
        if not rating_col or rating_col not in self.enriched_data.columns:
            logger.warning("Rating column not found, skipping composite score calculation")
            return
        
        # Normalize rating (0-1 scale)
        max_rating = self.enriched_data[rating_col].max()
        if max_rating > 0:
            rating_normalized = self.enriched_data[rating_col] / max_rating
        else:
            rating_normalized = self.enriched_data[rating_col]
        
        # Normalize review count
        max_reviews = self.enriched_data['review_count'].max()
        if max_reviews > 0:
            review_normalized = self.enriched_data['review_count'] / max_reviews
        else:
            review_normalized = 0
        
        # Calculate composite score (weighted combination)
        # Rating: 40%, Review Count: 30%, Popularity: 30% (if available)
        composite_score = (
            rating_normalized * 0.4 +
            review_normalized * 0.3
        )
        
        # Add popularity component if available
        if 'popularity_score' in self.enriched_data.columns:
            composite_score += self.enriched_data['popularity_score'] * 0.3
        else:
            composite_score += (rating_normalized + review_normalized) / 2 * 0.3
        
        # Ensure score is between 0 and 1
        composite_score = np.clip(composite_score, 0, 1)
        
        self.enriched_data['enriched_composite_score'] = composite_score
    
    def _extract_key_features(self) -> None:
        """Extract key features for each restaurant"""
        logger.info("Extracting key features")
        
        # Create feature summary
        features = []
        
        for idx, row in self.enriched_data.iterrows():
            feature_list = []
            
            # Rating feature
            rating_col = None
            for col in self.enriched_data.columns:
                if 'rating' in col.lower():
                    rating_col = col
                    break
            
            if rating_col and pd.notna(row[rating_col]):
                rating = row[rating_col]
                if rating >= 4.5:
                    feature_list.append("Highly Rated")
                elif rating >= 4.0:
                    feature_list.append("Well Rated")
            
            # Review count feature
            if 'review_count' in row and row['review_count'] > 100:
                feature_list.append("Popular")
            elif 'review_count' in row and row['review_count'] > 50:
                feature_list.append("Well Reviewed")
            
            # Cuisine feature
            cuisine_col = None
            for col in self.enriched_data.columns:
                if 'primary_cuisine' in col.lower():
                    cuisine_col = col
                    break
            
            if cuisine_col and pd.notna(row[cuisine_col]):
                feature_list.append(f"{row[cuisine_col]} Cuisine")
            
            # Price range feature
            price_col = None
            for col in self.enriched_data.columns:
                if 'price_range' in col.lower():
                    price_col = col
                    break
            
            if price_col and pd.notna(row[price_col]):
                feature_list.append(f"{row[price_col]} Price")
            
            features.append(", ".join(feature_list) if feature_list else "Standard")
        
        self.enriched_data['key_features'] = features
    
    def prepare_for_llm(self, max_restaurants: int = 50) -> List[Dict]:
        """
        Prepare enriched data for LLM processing
        
        Args:
            max_restaurants: Maximum number of restaurants to include
            
        Returns:
            List of dictionaries with restaurant information
        """
        logger.info(f"Preparing {max_restaurants} restaurants for LLM")
        
        if self.enriched_data is None or self.enriched_data.empty:
            return []
        
        # Select top restaurants by composite score
        data = self.enriched_data.copy()
        
        if 'enriched_composite_score' in data.columns:
            data = data.sort_values('enriched_composite_score', ascending=False)
        elif 'composite_score' in data.columns:
            data = data.sort_values('composite_score', ascending=False)
        
        data = data.head(max_restaurants)
        
        # Prepare structured data
        llm_data = []
        
        for idx, row in data.iterrows():
            restaurant_info = {
                'restaurant_id': row.get('restaurant_id', idx),
                'name': row.get('restaurant_name', row.get('name', 'Unknown')),
                'city': row.get('city', 'Unknown'),
                'cuisine': row.get('primary_cuisine', row.get('cuisine', 'Unknown')),
                'rating': float(row.get('normalized_rating', row.get('rating', 0))),
                'review_count': int(row.get('review_count', 0)),
                'price_range': row.get('price_range', 'Unknown'),
                'key_features': row.get('key_features', ''),
                'composite_score': float(row.get('enriched_composite_score', row.get('composite_score', 0)))
            }
            
            llm_data.append(restaurant_info)
        
        logger.info(f"Prepared {len(llm_data)} restaurants for LLM")
        
        return llm_data
    
    def get_enriched_data(self) -> Optional[pd.DataFrame]:
        """Get enriched data"""
        return self.enriched_data
    
    def get_enrichment_stats(self) -> Dict:
        """Get enrichment statistics"""
        if self.enriched_data is None or self.enriched_data.empty:
            return {}
        
        stats = {
            'total_restaurants': len(self.enriched_data),
            'has_composite_score': 'enriched_composite_score' in self.enriched_data.columns,
            'has_key_features': 'key_features' in self.enriched_data.columns,
            'average_composite_score': float(self.enriched_data['enriched_composite_score'].mean()) if 'enriched_composite_score' in self.enriched_data.columns else 0,
            'average_rating': float(self.enriched_data['normalized_rating'].mean()) if 'normalized_rating' in self.enriched_data.columns else 0,
            'total_reviews': int(self.enriched_data['review_count'].sum()) if 'review_count' in self.enriched_data.columns else 0
        }
        
        return stats
