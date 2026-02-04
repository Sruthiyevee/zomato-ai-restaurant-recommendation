"""
Data Cleaner Module for Phase 1
Handles comprehensive data cleaning operations
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZomatoDataCleaner:
    """Cleans Zomato restaurant dataset"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the data cleaner
        
        Args:
            data: Raw pandas DataFrame to clean
        """
        self.raw_data = data.copy()
        self.cleaned_data = None
        self.cleaning_stats = {}
        
    def clean(self) -> pd.DataFrame:
        """
        Perform comprehensive data cleaning
        
        Returns:
            Cleaned pandas DataFrame
        """
        logger.info("Starting data cleaning process...")
        self.cleaned_data = self.raw_data.copy()
        
        # Track initial state
        initial_count = len(self.cleaned_data)
        
        # Step 1: Handle missing values
        self._handle_missing_values()
        
        # Step 2: Remove duplicates
        self._remove_duplicates()
        
        # Step 3: Normalize text fields
        self._normalize_text_fields()
        
        # Step 4: Validate and clean data types
        self._clean_data_types()
        
        # Step 5: Handle outliers
        self._handle_outliers()
        
        # Step 6: Clean text data (reviews, descriptions)
        self._clean_text_data()
        
        # Step 7: Standardize categorical fields
        self._standardize_categoricals()
        
        # Calculate cleaning statistics
        final_count = len(self.cleaned_data)
        self.cleaning_stats = {
            'initial_count': initial_count,
            'final_count': final_count,
            'removed_count': initial_count - final_count,
            'removal_percentage': ((initial_count - final_count) / initial_count * 100) if initial_count > 0 else 0
        }
        
        logger.info(f"Data cleaning completed. Removed {self.cleaning_stats['removed_count']} records ({self.cleaning_stats['removal_percentage']:.2f}%)")
        
        return self.cleaned_data
    
    def _handle_missing_values(self) -> None:
        """Handle missing values in the dataset"""
        logger.info("Handling missing values...")
        
        # Identify critical fields (must have values)
        critical_fields = []
        if 'name' in self.cleaned_data.columns:
            critical_fields.append('name')
        if 'restaurant_name' in self.cleaned_data.columns:
            critical_fields.append('restaurant_name')
        if 'city' in self.cleaned_data.columns:
            critical_fields.append('city')
        
        # Remove rows with missing critical fields
        if critical_fields:
            before = len(self.cleaned_data)
            self.cleaned_data = self.cleaned_data.dropna(subset=critical_fields)
            after = len(self.cleaned_data)
            logger.info(f"Removed {before - after} rows with missing critical fields")
        
        # Handle missing ratings - set to 0 or median
        rating_columns = [col for col in self.cleaned_data.columns if 'rating' in col.lower() or 'rate' in col.lower()]
        for col in rating_columns:
            if self.cleaned_data[col].dtype in [np.float64, np.int64]:
                median_rating = self.cleaned_data[col].median()
                self.cleaned_data[col].fillna(median_rating if not pd.isna(median_rating) else 0, inplace=True)
        
        # Handle missing price range - set to 'Unknown' or most common
        price_columns = [col for col in self.cleaned_data.columns if 'price' in col.lower() or 'cost' in col.lower()]
        for col in price_columns:
            if self.cleaned_data[col].dtype == 'object':
                most_common = self.cleaned_data[col].mode()[0] if len(self.cleaned_data[col].mode()) > 0 else 'Unknown'
                self.cleaned_data[col].fillna(most_common, inplace=True)
        
        # Handle missing review text - set to empty string
        review_columns = [col for col in self.cleaned_data.columns if 'review' in col.lower() or 'text' in col.lower()]
        for col in review_columns:
            if self.cleaned_data[col].dtype == 'object':
                self.cleaned_data[col].fillna('', inplace=True)
    
    def _remove_duplicates(self) -> None:
        """Remove duplicate restaurant entries"""
        logger.info("Removing duplicates...")
        
        before = len(self.cleaned_data)
        
        # Try to identify restaurant identifier columns
        id_columns = []
        if 'restaurant_id' in self.cleaned_data.columns:
            id_columns = ['restaurant_id']
        elif 'id' in self.cleaned_data.columns:
            id_columns = ['id']
        else:
            # Use name and location for duplicate detection
            name_col = None
            city_col = None
            
            for col in ['name', 'restaurant_name', 'Name', 'Restaurant Name']:
                if col in self.cleaned_data.columns:
                    name_col = col
                    break
            
            for col in ['city', 'City', 'location', 'Location']:
                if col in self.cleaned_data.columns:
                    city_col = col
                    break
            
            if name_col and city_col:
                # Remove duplicates based on name and city
                self.cleaned_data = self.cleaned_data.drop_duplicates(subset=[name_col, city_col], keep='first')
            else:
                # Fallback: remove all duplicates
                self.cleaned_data = self.cleaned_data.drop_duplicates(keep='first')
        
        if id_columns:
            self.cleaned_data = self.cleaned_data.drop_duplicates(subset=id_columns, keep='first')
        
        after = len(self.cleaned_data)
        logger.info(f"Removed {before - after} duplicate records")
    
    def _normalize_text_fields(self) -> None:
        """Normalize text fields (remove extra spaces, special characters)"""
        logger.info("Normalizing text fields...")
        
        text_columns = self.cleaned_data.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            if col in self.cleaned_data.columns:
                # Remove extra whitespace
                self.cleaned_data[col] = self.cleaned_data[col].astype(str).str.strip()
                # Replace multiple spaces with single space
                self.cleaned_data[col] = self.cleaned_data[col].str.replace(r'\s+', ' ', regex=True)
                # Handle empty strings
                self.cleaned_data[col] = self.cleaned_data[col].replace('nan', '')
    
    def _clean_data_types(self) -> None:
        """Validate and clean data types"""
        logger.info("Cleaning data types...")
        
        # Clean specific 'rate' column if it exists (format: "4.1/5", "NEW", "-")
        if 'rate' in self.cleaned_data.columns:
            # Remove "/5" suffix
            self.cleaned_data['rate'] = self.cleaned_data['rate'].astype(str).str.replace('/5', '', regex=False)
            # Remove "NEW" and "-" (replace with NaN or 0)
            self.cleaned_data['rate'] = self.cleaned_data['rate'].replace(['NEW', '-', 'nan', 'None'], np.nan)
            # Clean any other non-numeric chars but keep decimal points
            # self.cleaned_data['rate'] = self.cleaned_data['rate'].str.extract(r'(\d+\.?\d*)')[0]

        # Convert rating columns to float
        rating_columns = [col for col in self.cleaned_data.columns if 'rating' in col.lower() or 'rate' in col.lower()]
        for col in rating_columns:
            if col in self.cleaned_data.columns:
                self.cleaned_data[col] = pd.to_numeric(self.cleaned_data[col], errors='coerce')
                # Ensure ratings are between 0 and 5
                if self.cleaned_data[col].dtype in [np.float64, np.int64]:
                    self.cleaned_data[col] = self.cleaned_data[col].clip(lower=0, upper=5)
        
        # Convert review count to integer
        review_count_columns = [col for col in self.cleaned_data.columns if 'review' in col.lower() and 'count' in col.lower()]
        for col in review_count_columns:
            if col in self.cleaned_data.columns:
                self.cleaned_data[col] = pd.to_numeric(self.cleaned_data[col], errors='coerce').fillna(0).astype(int)
        
        # Convert coordinates to float
        coord_columns = [col for col in self.cleaned_data.columns if 'lat' in col.lower() or 'lon' in col.lower() or 'latitude' in col.lower() or 'longitude' in col.lower()]
        for col in coord_columns:
            if col in self.cleaned_data.columns:
                self.cleaned_data[col] = pd.to_numeric(self.cleaned_data[col], errors='coerce')
    
    def _handle_outliers(self) -> None:
        """Handle outliers in numerical fields"""
        logger.info("Handling outliers...")
        
        # Handle rating outliers
        rating_columns = [col for col in self.cleaned_data.columns if 'rating' in col.lower() or 'rate' in col.lower()]
        for col in rating_columns:
            if col in self.cleaned_data.columns and self.cleaned_data[col].dtype in [np.float64, np.int64]:
                # Ratings should be between 0 and 5
                before_outliers = (self.cleaned_data[col] < 0) | (self.cleaned_data[col] > 5)
                self.cleaned_data.loc[before_outliers, col] = np.nan
                self.cleaned_data[col].fillna(self.cleaned_data[col].median(), inplace=True)
        
        # Handle review count outliers (remove extremely high values)
        review_count_columns = [col for col in self.cleaned_data.columns if 'review' in col.lower() and 'count' in col.lower()]
        for col in review_count_columns:
            if col in self.cleaned_data.columns and self.cleaned_data[col].dtype in [np.int64, np.float64]:
                # Cap at 99th percentile
                q99 = self.cleaned_data[col].quantile(0.99)
                self.cleaned_data.loc[self.cleaned_data[col] > q99, col] = q99
    
    def _clean_text_data(self) -> None:
        """Clean text data (reviews, descriptions)"""
        logger.info("Cleaning text data...")
        
        text_columns = [col for col in self.cleaned_data.columns if 'review' in col.lower() or 'text' in col.lower() or 'description' in col.lower()]
        
        for col in text_columns:
            if col in self.cleaned_data.columns:
                # Remove HTML tags
                self.cleaned_data[col] = self.cleaned_data[col].astype(str).str.replace(r'<[^>]+>', '', regex=True)
                # Remove special characters but keep basic punctuation
                self.cleaned_data[col] = self.cleaned_data[col].str.replace(r'[^\w\s.,!?;:\-\']', '', regex=True)
                # Normalize whitespace
                self.cleaned_data[col] = self.cleaned_data[col].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    def _standardize_categoricals(self) -> None:
        """Standardize categorical fields"""
        logger.info("Standardizing categorical fields...")
        
        # Standardize city names (lowercase, remove extra spaces)
        city_columns = [col for col in self.cleaned_data.columns if 'city' in col.lower()]
        for col in city_columns:
            if col in self.cleaned_data.columns:
                self.cleaned_data[col] = self.cleaned_data[col].astype(str).str.lower().str.strip().str.title()
        
        # Standardize cuisine names
        cuisine_columns = [col for col in self.cleaned_data.columns if 'cuisine' in col.lower()]
        for col in cuisine_columns:
            if col in self.cleaned_data.columns:
                self.cleaned_data[col] = self.cleaned_data[col].astype(str).str.strip()
                # Normalize common variations
                self.cleaned_data[col] = self.cleaned_data[col].str.replace('&', 'and', regex=False)
                self.cleaned_data[col] = self.cleaned_data[col].str.replace(r'\s+', ' ', regex=True)
        
        # Standardize price range
        price_columns = [col for col in self.cleaned_data.columns if 'price' in col.lower()]
        for col in price_columns:
            if col in self.cleaned_data.columns:
                # Normalize price range values
                self.cleaned_data[col] = self.cleaned_data[col].astype(str).str.strip()
                # Map common variations
                price_mapping = {
                    'budget': 'Budget',
                    'low': 'Budget',
                    'cheap': 'Budget',
                    'mid': 'Mid-Range',
                    'medium': 'Mid-Range',
                    'moderate': 'Mid-Range',
                    'premium': 'Premium',
                    'high': 'Premium',
                    'expensive': 'Premium',
                    'luxury': 'Luxury',
                    'very expensive': 'Luxury'
                }
                self.cleaned_data[col] = self.cleaned_data[col].str.lower().map(price_mapping).fillna(self.cleaned_data[col])
    
    def get_cleaning_stats(self) -> Dict:
        """Get statistics about the cleaning process"""
        return self.cleaning_stats.copy()
    
    def get_cleaned_data(self) -> Optional[pd.DataFrame]:
        """Get the cleaned data"""
        return self.cleaned_data
