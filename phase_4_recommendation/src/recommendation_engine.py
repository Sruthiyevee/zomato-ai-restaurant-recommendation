"""
Recommendation Engine Module for Phase 4
Main engine that integrates Groq LLM for restaurant recommendations
"""

import logging
import json
from typing import List, Dict, Optional, Tuple
from enum import Enum

from groq_client import GroqClient
from prompt_builder import PromptBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Main recommendation engine using Groq LLM"""
    
    def __init__(
        self,
        groq_client: Optional[GroqClient] = None,
        prompt_builder: Optional[PromptBuilder] = None
    ):
        """
        Initialize recommendation engine
        
        Args:
            groq_client: Optional GroqClient instance (creates new if not provided)
            prompt_builder: Optional PromptBuilder instance (creates new if not provided)
        """
        self.groq_client = groq_client or GroqClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.recommendation_history = []
        
    def generate_recommendations(
        self,
        restaurants: List[Dict],
        city: str,
        price_range: str,
        max_recommendations: int = 10
    ) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Generate restaurant recommendations using Groq LLM
        
        Args:
            restaurants: List of restaurant dictionaries from Phase 3
            city: User's selected city
            price_range: User's selected price range
            max_recommendations: Maximum number of recommendations
            
        Returns:
            Tuple of (success, recommendations_list, error_message)
        """
        try:
            logger.info(f"Generating recommendations for {city}, {price_range}")
            
            # Validate input data
            if not restaurants:
                return False, None, "No restaurants provided"
            
            if not self.prompt_builder.validate_restaurant_data(restaurants):
                return False, None, "Invalid restaurant data structure"
            
            # STRICT FILTERING: Filter by price range first
            # Normalize input price range
            target_price = price_range.lower().strip()
            
            # Filter restaurants matching the price range
            filtered_restaurants = [
                r for r in restaurants 
                if str(r.get('price_range', '')).lower().strip() == target_price
            ]
            
            # Fallback: If too few results (<5), use original list (or you could implement adjacent logic)
            if len(filtered_restaurants) < 5:
                logger.warning(f"Only found {len(filtered_restaurants)} restaurants for {price_range}. Using all price ranges as fallback.")
                context_candidates = restaurants
            else:
                logger.info(f"Filtered down to {len(filtered_restaurants)} restaurants matching {price_range}")
                context_candidates = filtered_restaurants

            # Context Optimization: Limit valid restaurants to top 50 by composite score
            # to avoid exceeding LLM context window (12k restaurants is too many)
            context_candidates.sort(key=lambda x: x.get('composite_score', 0) or 0, reverse=True)
            context_restaurants = context_candidates[:50]
            
            # Build prompt
            prompt = self.prompt_builder.build_recommendation_prompt(
                restaurants=context_restaurants,
                city=city,
                price_range=price_range,
                max_recommendations=max_recommendations
            )


            
            system_prompt = self.prompt_builder.get_system_prompt()
            
            # Generate recommendations using Groq
            logger.info("Calling Groq LLM for recommendations")
            response_text = self.groq_client.generate_recommendations(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            # Parse response
            recommendations = self._parse_llm_response(response_text, restaurants)
            
            if not recommendations:
                # Try fallback parsing
                recommendations = self._parse_fallback_response(response_text, restaurants)
            
            if not recommendations:
                return False, None, "Failed to parse LLM response"
            
            # Validate recommendations
            validated_recommendations = self._validate_recommendations(
                recommendations,
                restaurants,
                max_recommendations
            )
            
            # Store in history
            self.recommendation_history.append({
                'city': city,
                'price_range': price_range,
                'count': len(validated_recommendations),
                'restaurants': validated_recommendations
            })
            
            logger.info(f"Successfully generated {len(validated_recommendations)} recommendations")
            
            return True, validated_recommendations, None
            
        except Exception as e:
            error_msg = f"Error generating recommendations: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, None, error_msg
    
    def _parse_llm_response(self, response_text: str, restaurants: List[Dict]) -> List[Dict]:
        """
        Parse LLM JSON response
        
        Args:
            response_text: Raw response text from LLM
            restaurants: Original restaurant list for validation
            
        Returns:
            List of recommendation dictionaries
        """
        try:
            # Try to extract JSON from response
            # Look for JSON array in the response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                recommendations = json.loads(json_text)
                
                if isinstance(recommendations, list):
                    return recommendations
            
            # Try parsing entire response as JSON
            recommendations = json.loads(response_text)
            if isinstance(recommendations, list):
                return recommendations
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from response: {str(e)}")
        
        return []
    
    def _parse_fallback_response(self, response_text: str, restaurants: List[Dict]) -> List[Dict]:
        """
        Fallback parsing for non-JSON responses
        
        Args:
            response_text: Raw response text
            restaurants: Original restaurant list
            
        Returns:
            List of recommendation dictionaries
        """
        # Simple fallback: rank restaurants by composite score
        logger.info("Using fallback ranking method")
        
        # Sort restaurants by composite score
        sorted_restaurants = sorted(
            restaurants,
            key=lambda x: x.get('composite_score', x.get('rating', 0)),
            reverse=True
        )
        
        recommendations = []
        for i, restaurant in enumerate(sorted_restaurants[:10], 1):
            recommendations.append({
                'rank': i,
                'restaurant_name': restaurant.get('name', 'Unknown'),
                'cuisine': restaurant.get('cuisine', 'Unknown'),
                'rating': float(restaurant.get('rating', 0)),
                'price_range': restaurant.get('price_range', 'Unknown'),
                'reasoning': f"High quality score ({restaurant.get('composite_score', 0):.2f}) and rating ({restaurant.get('rating', 0):.2f})",
                'key_highlights': restaurant.get('key_features', '')
            })
        
        return recommendations
    
    def _validate_recommendations(
        self,
        recommendations: List[Dict],
        restaurants: List[Dict],
        max_count: int
    ) -> List[Dict]:
        """
        Validate and clean recommendations
        
        Args:
            recommendations: Raw recommendations from LLM
            restaurants: Original restaurant list
            max_count: Maximum number of recommendations
            
        Returns:
            Validated recommendations list
        """
        validated = []
        # Create a lookup map for faster access
        restaurant_map = {r.get('name', '').lower(): r for r in restaurants}
        
        for rec in recommendations[:max_count]:
            # Ensure required fields exist
            if 'restaurant_name' not in rec and 'name' not in rec:
                continue
            
            name = rec.get('restaurant_name') or rec.get('name', '')
            
            # Verify restaurant exists in original list
            if name.lower() not in restaurant_map:
                logger.warning(f"Recommendation '{name}' not found in original restaurant list")
                continue
            
            original_restaurant = restaurant_map[name.lower()]
            
            # Ensure all required fields - PREFER SOURCE OF TRUTH over LLM
            validated_rec = {
                'rank': rec.get('rank', len(validated) + 1),
                'restaurant_name': original_restaurant.get('name', name),
                'cuisine': original_restaurant.get('cuisine', rec.get('cuisine', 'Unknown')),
                # Use float() on the original rating which we know is valid from Phase 1/3
                'rating': float(original_restaurant.get('rating') or original_restaurant.get('normalized_rating') or 0),
                'price_range': original_restaurant.get('price_range', rec.get('price_range', 'Unknown')),
                'reasoning': rec.get('reasoning', rec.get('key_highlights', '')),
                'key_highlights': rec.get('key_highlights', rec.get('reasoning', ''))
            }
            
            validated.append(validated_rec)
        
        return validated
    
    def get_recommendation_history(self) -> List[Dict]:
        """Get recommendation history"""
        return self.recommendation_history.copy()
    
    def test_groq_connection(self) -> bool:
        """Test Groq API connection"""
        return self.groq_client.test_connection()
