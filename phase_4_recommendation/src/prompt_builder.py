"""
Prompt Builder Module for Phase 4
Constructs prompts for Groq LLM recommendation generation
"""

import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds prompts for LLM recommendation generation"""
    
    def __init__(self):
        """Initialize prompt builder"""
        self.system_role = self._get_system_role()
    
    def _get_system_role(self) -> str:
        """Get system role definition"""
        return """You are an expert restaurant recommendation assistant with deep knowledge 
of dining experiences, cuisines, and local food culture. Your expertise includes understanding 
restaurant quality, value, and matching restaurants to user preferences. Your role is to provide 
personalized, well-reasoned restaurant recommendations based on user preferences and comprehensive 
restaurant data."""
    
    def build_recommendation_prompt(
        self,
        restaurants: List[Dict],
        city: str,
        price_range: str,
        max_recommendations: int = 10
    ) -> str:
        """
        Build prompt for restaurant recommendations
        
        Args:
            restaurants: List of restaurant dictionaries
            city: User's selected city
            price_range: User's selected price range
            max_recommendations: Maximum number of recommendations to generate
            
        Returns:
            Formatted prompt string
        """
        logger.info(f"Building recommendation prompt for {len(restaurants)} restaurants")
        
        # Build restaurant context section
        restaurant_context = self._build_restaurant_context(restaurants)
        
        # Build user preferences section
        user_preferences = self._build_user_preferences(city, price_range)
        
        # Build task definition
        task_definition = self._build_task_definition(max_recommendations)
        
        # Build output format specification
        output_format = self._build_output_format()
        
        # Combine all sections
        prompt = f"""{restaurant_context}

{user_preferences}

{task_definition}

{output_format}"""
        
        return prompt
    
    def _build_restaurant_context(self, restaurants: List[Dict]) -> str:
        """Build restaurant context section"""
        context_lines = ["RESTAURANT DATA:"]
        context_lines.append("=" * 60)
        
        for i, restaurant in enumerate(restaurants, 1):
            name = restaurant.get('name', 'Unknown')
            cuisine = restaurant.get('cuisine', 'Unknown')
            rating = restaurant.get('rating', 0)
            review_count = restaurant.get('review_count', 0)
            price_range = restaurant.get('price_range', 'Unknown')
            key_features = restaurant.get('key_features', '')
            composite_score = restaurant.get('composite_score', 0)
            
            context_lines.append(f"\nRestaurant {i}:")
            context_lines.append(f"  Name: {name}")
            context_lines.append(f"  Cuisine: {cuisine}")
            context_lines.append(f"  Rating: {rating:.2f}/5.0")
            context_lines.append(f"  Review Count: {review_count}")
            context_lines.append(f"  Price Range: {price_range}")
            context_lines.append(f"  Key Features: {key_features}")
            context_lines.append(f"  Quality Score: {composite_score:.2f}")
        
        context_lines.append("\n" + "=" * 60)
        
        return "\n".join(context_lines)
    
    def _build_user_preferences(self, city: str, price_range: str) -> str:
        """Build user preferences section"""
        return f"""USER PREFERENCES:
- City: {city}
- Price Range: {price_range}

Please recommend restaurants that match these preferences."""
    
    def _build_task_definition(self, max_recommendations: int) -> str:
        """Build task definition section"""
        return f"""TASK:
Rank and recommend the top {max_recommendations} restaurants from the provided list that best match 
the user's preferences. Consider the following factors:
1. Exact match to price range and city
2. High ratings and positive review sentiment
3. Value proposition (quality-to-price ratio)
4. Unique features and specialties
5. Diversity in cuisine types and dining experiences

IMPORTANT CONSTRAINTS:
- Only recommend restaurants from the provided list above
- Do not invent restaurants or details not in the data
- Base recommendations solely on the provided information
- Ensure variety in recommendations (different cuisines, experiences)"""
    
    def _build_output_format(self) -> str:
        """Build output format specification"""
        return """OUTPUT FORMAT:
Provide your recommendations as a JSON array with the following structure:
[
  {{
    "rank": 1,
    "restaurant_name": "Restaurant Name",
    "cuisine": "Cuisine Type",
    "rating": 4.5,
    "price_range": "Price Range",
    "reasoning": "Brief explanation of why this restaurant is recommended",
    "key_highlights": "Notable features or specialties"
  }},
  ...
]

Ensure the JSON is valid and properly formatted. Rank restaurants from 1 (best match) to {max_recommendations}."""
    
    def get_system_prompt(self) -> str:
        """Get system prompt for LLM"""
        return self.system_role
    
    def build_fallback_prompt(self, restaurants: List[Dict], city: str, price_range: str) -> str:
        """
        Build a simpler prompt for fallback scenarios
        
        Args:
            restaurants: List of restaurant dictionaries
            city: User's selected city
            price_range: User's selected price range
            
        Returns:
            Simplified prompt string
        """
        restaurant_list = "\n".join([
            f"- {r.get('name', 'Unknown')} ({r.get('cuisine', 'Unknown')}, Rating: {r.get('rating', 0):.1f})"
            for r in restaurants[:20]  # Limit for simpler prompt
        ])
        
        return f"""Recommend top restaurants in {city} with {price_range} price range from this list:

{restaurant_list}

Provide 5-10 recommendations with brief reasoning for each."""
    
    def validate_restaurant_data(self, restaurants: List[Dict]) -> bool:
        """
        Validate restaurant data structure
        
        Args:
            restaurants: List of restaurant dictionaries
            
        Returns:
            True if valid, False otherwise
        """
        if not restaurants:
            return False
        
        required_fields = ['name', 'cuisine', 'rating', 'price_range']
        
        for restaurant in restaurants:
            for field in required_fields:
                if field not in restaurant:
                    logger.warning(f"Missing required field '{field}' in restaurant data")
                    return False
        
        return True
