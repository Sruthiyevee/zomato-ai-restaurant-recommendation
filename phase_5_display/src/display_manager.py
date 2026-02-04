"""
Display Manager Module for Phase 5
Handles all formatting and rendering of text to the terminal.
"""

import math
from typing import List, Dict, Any, Optional

class DisplayManager:
    """Manages CLI output formatting and display"""
    
    def __init__(self):
        """Initialize display manager"""
        self.width = 60
        self.header_border = "═" * self.width
        self.section_border = "─" * self.width
        
    def print_header(self):
        """Display application banner"""
        print(f"\n{self.header_border}")
        print("    ZOMATO AI RESTAURANT RECOMMENDATIONS")
        print(f"{self.header_border}\n")
        
    def _get_star_rating(self, rating: float) -> str:
        """Convert float rating to star representation"""
        try:
            full_stars = int(rating)
            half_star = 1 if (rating - full_stars) >= 0.5 else 0
            empty_stars = 5 - full_stars - half_star
            
            return "★" * full_stars + ("½" if half_star else "") + "☆" * empty_stars
        except (ValueError, TypeError):
            return "☆☆☆☆☆"
            
    def format_price(self, price_range: str) -> str:
        """Add visual indicator to price range"""
        price_map = {
            'Budget': '$',
            'Mid-Range': '$$',
            'Premium': '$$$',
            'Luxury': '$$$$'
        }
        symbol = price_map.get(price_range, '')
        return f"{price_range} ({symbol})" if symbol else price_range

    def display_recommendations(self, recommendations: List[Dict[str, Any]], city: str, price_range: str):
        """
        Render list of recommendations with ASCII styling
        
        Args:
            recommendations: List of recommendation dictionaries
            city: User selected city
            price_range: User selected price range
        """
        print(f"City: {city}")
        print(f"Price Range: {self.format_price(price_range)}")
        print(f"Recommendations: {len(recommendations)}")
        print(f"\n{self.section_border}")
        
        if not recommendations:
            print("\nNo recommendations found matching your criteria.")
            print("Try adjusting your search filters.")
            print(f"\n{self.header_border}")
            return

        for i, rec in enumerate(recommendations, 1):
            self.format_single_recommendation(rec, i)
            print(f"\n{self.section_border}")
            
        print(f"{self.header_border}")

    def format_single_recommendation(self, rec: Dict[str, Any], rank: int):
        """
        Formats individual recommendation details
        
        Args:
            rec: Recommendation dictionary
            rank: Rank number
        """
        # Extract data with safe defaults
        name = rec.get('restaurant_name', 'Unknown Restaurant')
        cuisine = rec.get('cuisine', 'Unknown Cuisine')
        rating = rec.get('rating', 0.0)
        reviews = rec.get('review_count', 0)
        price = rec.get('price_range', 'Unknown Price')
        reasoning = rec.get('reasoning', 'No reasoning provided.')
        features = rec.get('key_features', [])
        
        # Format strings
        star_str = self._get_star_rating(float(rating))
        
        # Display
        print(f"\n#{rank} {name.upper()}")
        print(f"   Cuisine: {cuisine}")
        print(f"   Rating: {star_str} ({rating}/5.0) | Reviews: {reviews}")
        print(f"   Price: {price}")
        
        print("\n   Why Recommended:")
        # Wrap reasoning text for better readability
        words = reasoning.split()
        current_line = "   "
        for word in words:
            if len(current_line) + len(word) + 1 > self.width:
                print(current_line)
                current_line = "   " + word
            else:
                current_line += " " + word
        print(current_line)
        
        if features:
            print("\n   Key Features: " + ", ".join(features))

    def display_error(self, message: str):
        """Standardized error output"""
        print(f"\n❌ ERROR: {message}\n")
        
    def display_loading(self, message: str = "Processing..."):
        """Display loading message"""
        print(f"\n⏳ {message}")
        
    def display_success(self, message: str):
        """Display success message"""
        print(f"\n✅ {message}")
