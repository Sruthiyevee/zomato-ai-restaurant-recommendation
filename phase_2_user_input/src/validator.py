"""
Input Validator Module for Phase 2
Handles validation of user inputs (city and price range)
"""

import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceRange(Enum):
    """Price range categories"""
    BUDGET = "Budget"
    MID_RANGE = "Mid-Range"
    PREMIUM = "Premium"
    LUXURY = "Luxury"


class InputValidator:
    """Validates user inputs for city and price range"""
    
    def __init__(self, available_cities: Optional[List[str]] = None):
        """
        Initialize the validator
        
        Args:
            available_cities: List of available cities from dataset
        """
        self.available_cities = [city.lower() if city else "" for city in (available_cities or [])]
        self.price_ranges = [pr.value for pr in PriceRange]
        self.price_range_mapping = {
            '1': PriceRange.BUDGET,
            '2': PriceRange.MID_RANGE,
            '3': PriceRange.PREMIUM,
            '4': PriceRange.LUXURY,
            'budget': PriceRange.BUDGET,
            'mid-range': PriceRange.MID_RANGE,
            'mid range': PriceRange.MID_RANGE,
            'premium': PriceRange.PREMIUM,
            'luxury': PriceRange.LUXURY,
            'low': PriceRange.BUDGET,
            'medium': PriceRange.MID_RANGE,
            'high': PriceRange.PREMIUM,
            'very high': PriceRange.LUXURY
        }
    
    def validate_city(self, city: str) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """
        Validate city input
        
        Args:
            city: City name to validate
            
        Returns:
            Tuple of (is_valid, normalized_city, suggestions)
        """
        if not city or not isinstance(city, str):
            return False, None, None
        
        city_clean = city.strip()
        if not city_clean:
            return False, None, None
        
        city_lower = city_clean.lower()
        
        # Exact match
        if city_lower in self.available_cities:
            # Return original case from available cities
            original_city = next((c for c in (self.available_cities or []) if c.lower() == city_lower), city_clean)
            return True, original_city.title(), None
        
        # Fuzzy matching for typos
        suggestions = self._fuzzy_match_city(city_lower)
        if suggestions:
            return False, None, suggestions
        
        return False, None, None
    
    def _fuzzy_match_city(self, city: str, max_suggestions: int = 3) -> Optional[List[str]]:
        """
        Find fuzzy matches for city name
        
        Args:
            city: City name to match
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested city names
        """
        if not self.available_cities:
            return None
        
        suggestions = []
        city_len = len(city)
        
        for available_city in self.available_cities:
            if not available_city:
                continue
            
            # Check if city is a substring
            if city in available_city or available_city in city:
                suggestions.append(available_city.title())
                continue
            
            # Calculate similarity (simple Levenshtein-like)
            similarity = self._calculate_similarity(city, available_city)
            if similarity > 0.6:  # 60% similarity threshold
                suggestions.append(available_city.title())
        
        # Remove duplicates and limit
        suggestions = list(dict.fromkeys(suggestions))[:max_suggestions]
        return suggestions if suggestions else None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate simple similarity between two strings
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
        
        # Simple character overlap similarity
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def validate_price_range(self, price_input: str) -> Tuple[bool, Optional[PriceRange], Optional[str]]:
        """
        Validate price range input
        
        Args:
            price_input: Price range input (number or text)
            
        Returns:
            Tuple of (is_valid, price_range_enum, error_message)
        """
        if not price_input or not isinstance(price_input, str):
            return False, None, "Price range input is required"
        
        price_clean = price_input.strip().lower()
        
        # Check mapping
        if price_clean in self.price_range_mapping:
            return True, self.price_range_mapping[price_clean], None
        
        # Try numeric input
        try:
            price_num = int(price_clean)
            if 1 <= price_num <= 4:
                price_range = list(PriceRange)[price_num - 1]
                return True, price_range, None
        except ValueError:
            pass
        
        # Invalid input
        valid_options = ", ".join([f"{i+1}. {pr.value}" for i, pr in enumerate(PriceRange)])
        error_msg = f"Invalid price range. Valid options: {valid_options}"
        return False, None, error_msg
    
    def get_price_range_options(self) -> List[Dict[str, str]]:
        """
        Get formatted price range options for display
        
        Returns:
            List of dictionaries with number and description
        """
        options = []
        descriptions = {
            PriceRange.BUDGET: "Low-cost dining options",
            PriceRange.MID_RANGE: "Moderate pricing",
            PriceRange.PREMIUM: "Higher-end establishments",
            PriceRange.LUXURY: "Top-tier dining experiences"
        }
        
        for i, price_range in enumerate(PriceRange, 1):
            options.append({
                'number': str(i),
                'value': price_range.value,
                'description': descriptions.get(price_range, "")
            })
        
        return options
    
    def update_available_cities(self, cities: List[str]) -> None:
        """
        Update the list of available cities
        
        Args:
            cities: List of city names
        """
        self.available_cities = [city.lower() if city else "" for city in cities]
        logger.info(f"Updated available cities: {len(self.available_cities)} cities")
    
    def get_available_cities(self) -> List[str]:
        """
        Get list of available cities (in original case)
        
        Returns:
            List of city names
        """
        # Return cities in title case for display
        return [city.title() for city in self.available_cities if city]

