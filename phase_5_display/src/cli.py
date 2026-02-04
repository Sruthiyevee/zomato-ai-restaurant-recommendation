"""
CLI Module for Phase 5
Manages user interaction flow for the restaurant recommendation service.
"""

import sys
import os
import pandas as pd
from typing import Tuple, Optional, List, Dict

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Add Phase 4 src to path
PHASE_4_SRC = os.path.join(PROJECT_ROOT, 'phase_4_recommendation', 'src')
if PHASE_4_SRC not in sys.path:
    sys.path.append(PHASE_4_SRC)

# Add Phase 1 src to path
PHASE_1_SRC = os.path.join(PROJECT_ROOT, 'phase_1_data_ingestion', 'src')
if PHASE_1_SRC not in sys.path:
    sys.path.append(PHASE_1_SRC)
    
from storage import ZomatoDataStorage
from recommendation_engine import RecommendationEngine
from display_manager import DisplayManager

class CLI:
    """Manages CLI interactions and user flow"""
    
    def __init__(self):
        """Initialize CLI with display manager"""
        self.display = DisplayManager()
        self.valid_price_ranges = {
            '1': 'Budget',
            '2': 'Mid-Range',
            '3': 'Premium',
            '4': 'Luxury'
        }
        
        # Initialize Engine and Storage
        try:
            self.storage = ZomatoDataStorage()
            self.engine = RecommendationEngine()
            self.restaurants = self._load_data()
        except Exception as e:
            self.display.display_error(f"Initialization failed: {e}")
            self.restaurants = []
            
    def _load_data(self) -> List[Dict]:
        """Load and transform data from storage"""
        try:
            print("Loading restaurant data from database...", end="\r")
            df = self.storage.load_from_db()
            
            if df.empty:
                return []
            
            # Transform to format expected by Recommendation Engine
            restaurants = []
            for _, row in df.iterrows():
                restaurants.append({
                    'name': row.get('restaurant_name') or 'Unknown',
                    'cuisine': row.get('primary_cuisine') or 'Unknown',
                    'rating': float(row.get('normalized_rating') or 0.0),
                    'review_count': int(row.get('review_count') or 0),
                    'price_range': row.get('price_range') or 'Unknown',
                    'composite_score': float(row.get('composite_score') or 0.0),
                    'key_features': str(row.get('cuisine_list', '')) # Simple string conversion
                })
            
            print(f"Loaded {len(restaurants)} restaurants.           ")
            return restaurants
            
        except Exception as e:
            # Don't show error if DB just doesn't exist yet (first run)
            return []

    def start(self):
        """Start the CLI application"""
        self.display.print_header()
        
        if not self.restaurants:
            self.display.display_error("No restaurant data found.")
            self.display.display_loading("Running data ingestion pipeline (this may take a minute)...")
            # Optional: Trigger pipeline here? For now, just warn.
            print("Please ensure the data ingestion pipeline has been run.")
            # We can allow the user to continue if they want to try anyway (it will fail gracefuly)
            
        while True:
            # Get User Input
            city, price_range = self.get_user_inputs()
            if not city:
                self.display.display_success("Exiting application.")
                break
                
            # Valid Input Received
            self.display.display_loading(f"Finding top restaurants in {city} ({price_range})...")
            
            # Generate Recommendations
            success, recommendations, error = self.engine.generate_recommendations(
                restaurants=self.restaurants,
                city=city,
                price_range=price_range,
                max_recommendations=5
            )
            
            if success:
                self.display.display_recommendations(recommendations, city, price_range)
            else:
                self.display.display_error(error)
                
            # Verify Continue
            if not self.verify_continue():
                break

    def get_user_inputs(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Collect and validate user inputs
        
        Returns:
            Tuple of (city, price_range) or (None, None) if user exits
        """
        # Get City
        city = self._get_city_input()
        if not city:
            return None, None
            
        # Get Price Range
        price_range = self._get_price_input()
        if not price_range:
            return None, None
            
        return city, price_range
        
    def _get_city_input(self) -> Optional[str]:
        """Prompt for city input"""
        while True:
            try:
                city = input("Enter city name (or 'q' to quit): ").strip()
                
                if city.lower() == 'q':
                    return None
                    
                if not city:
                    self.display.display_error("City name cannot be empty.")
                    continue
                    
                if len(city) < 2:
                    self.display.display_error("City name is too short. Please enter a valid city.")
                    continue
                    
                # Basic validation passed
                return city.title()
                
            except KeyboardInterrupt:
                print("\n")
                return None
                
    def _get_price_input(self) -> Optional[str]:
        """Prompt for price range selection"""
        print("\nSelect Price Range:")
        print("1. Budget ($)")
        print("2. Mid-Range ($$)")
        print("3. Premium ($$$)")
        print("4. Luxury ($$$$)")
        
        while True:
            try:
                choice = input("\nEnter choice (1-4) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                    
                if choice in self.valid_price_ranges:
                    return self.valid_price_ranges[choice]
                    
                self.display.display_error("Invalid choice. Please enter a number between 1 and 4.")
                
            except KeyboardInterrupt:
                print("\n")
                return None

    def verify_continue(self) -> bool:
        """
        Ask user if they want to perform another search
        
        Returns:
            True to continue, False to exit
        """
        while True:
            try:
                choice = input("\nWould you like to search again? (y/n): ").strip().lower()
                
                if choice in ['y', 'yes']:
                    return True
                elif choice in ['n', 'no', 'q', 'quit']:
                    print("\nThank you for using Zomato AI Recommendations. Goodbye!")
                    return False
                else:
                    self.display.display_error("Please enter 'y' for yes or 'n' for no.")
                    
            except KeyboardInterrupt:
                return False

if __name__ == "__main__":
    # Simple test run if executed directly
    cli = CLI()
    cli.start()
    city, price = cli.get_user_inputs()
    if city and price:
        cli.display.display_success(f"Collected: {city}, {price}")
