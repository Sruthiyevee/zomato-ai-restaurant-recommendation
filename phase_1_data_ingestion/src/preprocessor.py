"""
Data Preprocessor Module for Phase 1
Handles feature engineering and data preprocessing
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZomatoDataPreprocessor:
    """Preprocesses cleaned Zomato restaurant data"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the preprocessor
        
        Args:
            data: Cleaned pandas DataFrame
        """
        self.cleaned_data = data.copy()
        self.processed_data = None
        self.preprocessing_stats = {}
        
    def preprocess(self) -> pd.DataFrame:
        """
        Perform comprehensive preprocessing
        
        Returns:
            Preprocessed pandas DataFrame
        """
        logger.info("Starting data preprocessing...")
        self.processed_data = self.cleaned_data.copy()
        
        # Step 1: Feature engineering
        self._engineer_features()
        
        # Step 2: Price range categorization
        self._categorize_price_range()
        
        # Step 3: Rating normalization
        self._normalize_ratings()
        
        # Step 4: Review aggregation
        self._aggregate_reviews()
        
        # Step 5: Popularity metrics
        self._calculate_popularity_metrics()
        
        # Step 6: Cuisine encoding
        self._encode_cuisines()
        
        # Step 7: Geospatial processing
        self._process_geospatial()
        
        # Step 8: Create composite scores
        self._create_composite_scores()
        
        logger.info("Data preprocessing completed")
        
        return self.processed_data
    
    def _engineer_features(self) -> None:
        """Engineer new features from existing data"""
        logger.info("Engineering features...")
        
        # Create restaurant identifier if not exists
        if 'restaurant_id' not in self.processed_data.columns:
            if 'id' in self.processed_data.columns:
                self.processed_data['restaurant_id'] = self.processed_data['id']
            else:
                self.processed_data['restaurant_id'] = range(1, len(self.processed_data) + 1)
        
        # Ensure restaurant name column exists
        if 'restaurant_name' not in self.processed_data.columns:
            name_col = None
            for col in ['name', 'Name', 'Restaurant Name']:
                if col in self.processed_data.columns:
                    name_col = col
                    break
            if name_col:
                self.processed_data['restaurant_name'] = self.processed_data[name_col]
        
        # Ensure city column exists
        if 'city' not in self.processed_data.columns:
            city_col = None
            for col in ['City', 'location', 'Location']:
                if col in self.processed_data.columns:
                    city_col = col
                    break
            if city_col:
                self.processed_data['city'] = self.processed_data[city_col]
            else:
                self.processed_data['city'] = 'Unknown'
                
        # Fill missing values
        self.processed_data['city'] = self.processed_data['city'].fillna('Unknown')
        self.processed_data['restaurant_name'] = self.processed_data['restaurant_name'].fillna('Unknown Restaurant')
    
    def _categorize_price_range(self) -> None:
        """Categorize price range into standardized buckets"""
        logger.info("Categorizing price ranges...")
        
        # Find price-related columns
        price_cols = [col for col in self.processed_data.columns if 'price' in col.lower() or 'cost' in col.lower()]
        
        if not price_cols:
            # Create default price range if not exists
            self.processed_data['price_range'] = 'Mid-Range'
            return
        
        price_col = price_cols[0]
        
        # Map to standard categories
        def map_price_range(value):
            if pd.isna(value):
                return 'Mid-Range'
            
            value_str = str(value).lower().strip()
            
            # Check for numeric indicators (e.g., 1-4, $ symbols)
            if '$' in value_str:
                dollar_count = value_str.count('$')
                if dollar_count == 1:
                    return 'Budget'
                elif dollar_count == 2:
                    return 'Mid-Range'
                elif dollar_count == 3:
                    return 'Premium'
                elif dollar_count >= 4:
                    return 'Luxury'
            
            # Check for numeric ranges
            if re.search(r'\d', value_str):
                if '1' in value_str or 'budget' in value_str or 'low' in value_str:
                    return 'Budget'
                elif '2' in value_str or 'mid' in value_str or 'medium' in value_str:
                    return 'Mid-Range'
                elif '3' in value_str or 'premium' in value_str or 'high' in value_str:
                    return 'Premium'
                elif '4' in value_str or 'luxury' in value_str or 'very' in value_str:
                    return 'Luxury'
            
            # Text-based mapping
            if any(word in value_str for word in ['budget', 'cheap', 'low', 'affordable']):
                return 'Budget'
            elif any(word in value_str for word in ['mid', 'medium', 'moderate', 'average']):
                return 'Mid-Range'
            elif any(word in value_str for word in ['premium', 'high', 'expensive']):
                return 'Premium'
            elif any(word in value_str for word in ['luxury', 'very expensive', 'upscale']):
                return 'Luxury'
            
            return 'Mid-Range'  # Default
        
        self.processed_data['price_range'] = self.processed_data[price_col].apply(map_price_range)
    
    def _normalize_ratings(self) -> None:
        """Normalize ratings to 0-5 scale"""
        logger.info("Normalizing ratings...")
        
        rating_cols = [col for col in self.processed_data.columns if 'rating' in col.lower() or 'rate' in col.lower()]
        
        for col in rating_cols:
            if col in self.processed_data.columns and self.processed_data[col].dtype in [np.float64, np.int64]:
                # Ensure ratings are between 0 and 5
                max_val = self.processed_data[col].max()
                if max_val > 5:
                    # Scale down if ratings are out of 10 or 100
                    if max_val <= 10:
                        self.processed_data[col] = self.processed_data[col] / 2
                    elif max_val <= 100:
                        self.processed_data[col] = self.processed_data[col] / 20
                
                # Ensure 0-5 range
                self.processed_data[col] = self.processed_data[col].clip(lower=0, upper=5)
        
        # Create normalized_rating column
        if rating_cols:
            main_rating_col = rating_cols[0]
            self.processed_data['normalized_rating'] = self.processed_data[main_rating_col]
        else:
            self.processed_data['normalized_rating'] = 0.0
    
    def _aggregate_reviews(self) -> None:
        """Aggregate review data"""
        logger.info("Aggregating reviews...")
        
        # Find review count column
        review_count_cols = [col for col in self.processed_data.columns if 'review' in col.lower() and 'count' in col.lower()]
        
        if review_count_cols:
            self.processed_data['review_count'] = pd.to_numeric(
                self.processed_data[review_count_cols[0]], errors='coerce'
            ).fillna(0).astype(int)
        else:
            self.processed_data['review_count'] = 0
        
        # Calculate review recency score (if date information available)
        date_cols = [col for col in self.processed_data.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            try:
                self.processed_data['last_review_date'] = pd.to_datetime(
                    self.processed_data[date_cols[0]], errors='coerce'
                )
                # Calculate days since last review
                if not self.processed_data['last_review_date'].isna().all():
                    latest_date = self.processed_data['last_review_date'].max()
                    self.processed_data['days_since_review'] = (
                        latest_date - self.processed_data['last_review_date']
                    ).dt.days
                    # Recency score (higher = more recent)
                    max_days = self.processed_data['days_since_review'].max()
                    if max_days > 0:
                        self.processed_data['recency_score'] = 1 - (
                            self.processed_data['days_since_review'] / max_days
                        )
                    else:
                        self.processed_data['recency_score'] = 1.0
                else:
                    self.processed_data['recency_score'] = 0.5
            except:
                self.processed_data['recency_score'] = 0.5
        else:
            self.processed_data['recency_score'] = 0.5  # Default neutral score
    
    def _calculate_popularity_metrics(self) -> None:
        """Calculate popularity scores"""
        logger.info("Calculating popularity metrics...")
        
        # Normalize review count for popularity score
        if 'review_count' in self.processed_data.columns:
            max_reviews = self.processed_data['review_count'].max()
            if max_reviews > 0:
                self.processed_data['review_count_normalized'] = (
                    self.processed_data['review_count'] / max_reviews
                )
            else:
                self.processed_data['review_count_normalized'] = 0
        else:
            self.processed_data['review_count_normalized'] = 0
        
        # Calculate popularity score (weighted combination)
        rating_weight = 0.6
        review_weight = 0.3
        recency_weight = 0.1
        
        self.processed_data['popularity_score'] = (
            (self.processed_data['normalized_rating'] / 5.0) * rating_weight +
            self.processed_data['review_count_normalized'] * review_weight +
            self.processed_data['recency_score'] * recency_weight
        )
    
    def _encode_cuisines(self) -> None:
        """Encode cuisine types"""
        logger.info("Encoding cuisines...")
        
        cuisine_cols = [col for col in self.processed_data.columns if 'cuisine' in col.lower()]
        
        if cuisine_cols:
            cuisine_col = cuisine_cols[0]
            # Create cuisine list (handle multiple cuisines separated by comma, &, etc.)
            self.processed_data['cuisine_list'] = self.processed_data[cuisine_col].astype(str).apply(
                lambda x: [c.strip() for c in re.split(r'[,&|]', str(x)) if c.strip() and str(c).strip().lower() != 'nan']
            )
            # Primary cuisine (first one)
            self.processed_data['primary_cuisine'] = self.processed_data['cuisine_list'].apply(
                lambda x: x[0] if len(x) > 0 else 'Unknown'
            )
            # Number of cuisines
            self.processed_data['cuisine_count'] = self.processed_data['cuisine_list'].apply(len)
        else:
            self.processed_data['primary_cuisine'] = 'Unknown'
            self.processed_data['cuisine_list'] = self.processed_data.apply(lambda x: [], axis=1)
            self.processed_data['cuisine_count'] = 0
    
    def _process_geospatial(self) -> None:
        """Process geospatial data"""
        logger.info("Processing geospatial data...")
        
        # Find coordinate columns
        lat_cols = [col for col in self.processed_data.columns if 'lat' in col.lower()]
        lon_cols = [col for col in self.processed_data.columns if 'lon' in col.lower()]
        
        if lat_cols and lon_cols:
            self.processed_data['latitude'] = pd.to_numeric(
                self.processed_data[lat_cols[0]], errors='coerce'
            )
            self.processed_data['longitude'] = pd.to_numeric(
                self.processed_data[lon_cols[0]], errors='coerce'
            )
        else:
            # Set default coordinates if not available
            self.processed_data['latitude'] = np.nan
            self.processed_data['longitude'] = np.nan
        
        # Validate coordinates (latitude: -90 to 90, longitude: -180 to 180)
        if 'latitude' in self.processed_data.columns:
            self.processed_data['latitude'] = self.processed_data['latitude'].clip(-90, 90)
        if 'longitude' in self.processed_data.columns:
            self.processed_data['longitude'] = self.processed_data['longitude'].clip(-180, 180)
    
    def _create_composite_scores(self) -> None:
        """Create composite quality scores"""
        logger.info("Creating composite scores...")
        
        # Composite score for ranking (used in filtering)
        # Weighted combination of rating, review count, and popularity
        rating_component = (self.processed_data['normalized_rating'] / 5.0) * 0.4
        review_component = self.processed_data['review_count_normalized'] * 0.3
        popularity_component = self.processed_data['popularity_score'] * 0.3
        
        self.processed_data['composite_score'] = (
            rating_component + review_component + popularity_component
        )
        
        # Ensure score is between 0 and 1
        self.processed_data['composite_score'] = self.processed_data['composite_score'].clip(0, 1)
    
    def get_processed_data(self) -> Optional[pd.DataFrame]:
        """Get the processed data"""
        return self.processed_data
    
    def get_preprocessing_stats(self) -> Dict:
        """Get preprocessing statistics"""
        if self.processed_data is not None:
            return {
                'total_restaurants': len(self.processed_data),
                'unique_cities': self.processed_data['city'].nunique() if 'city' in self.processed_data.columns else 0,
                'price_range_distribution': self.processed_data['price_range'].value_counts().to_dict() if 'price_range' in self.processed_data.columns else {},
                'average_rating': self.processed_data['normalized_rating'].mean() if 'normalized_rating' in self.processed_data.columns else 0,
                'total_reviews': self.processed_data['review_count'].sum() if 'review_count' in self.processed_data.columns else 0
            }
        return {}
