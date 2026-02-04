"""
CLI Handler Module for Phase 2
Handles command-line interface interactions for user input
"""

import logging
import sys
from typing import Dict, Optional, Tuple
from enum import Enum

from validator import InputValidator, PriceRange

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CLIHandler:
    """Handles CLI interactions for collecting user input"""
    
    def __init__(self, validator: InputValidator):
        """
        Initialize CLI handler
        
        Args:
            validator: InputValidator instance for validation
        """
        self.validator = validator
        self.max_retries = 3
    
    def display_welcome(self) -> None:
        """Display welcome message"""
        print("\n" + "=" * 60)
        print("  ZOMATO AI RESTAURANT RECOMMENDATION SERVICE")
        print("=" * 60)
        print("\nWelcome! I'll help you find the perfect restaurant.")
        print("Please provide the following information:\n")
    
    def collect_city(self) -> Optional[str]:
        """
        Collect and validate city input from user
        
        Returns:
            Validated city name or None if user cancels
        """
        retry_count = 0
        
        # Display available cities on first attempt
        if retry_count == 0:
            self._display_available_cities()
        
        while retry_count < self.max_retries:
            try:
                print("Enter city name: ", end="", flush=True)
                city_input = input().strip()
                
                if not city_input:
                    print("City name cannot be empty. Please try again.\n")
                    retry_count += 1
                    continue
                
                # Validate city
                is_valid, normalized_city, suggestions = self.validator.validate_city(city_input)
                
                if is_valid:
                    print(f"✓ City selected: {normalized_city}\n")
                    return normalized_city
                else:
                    if suggestions:
                        print(f"\nCity '{city_input}' not found. Did you mean:")
                        for i, suggestion in enumerate(suggestions, 1):
                            print(f"  {i}. {suggestion}")
                        print()
                    else:
                        # Show available cities again on error
                        print(f"\nCity '{city_input}' not found.")
                        print("Please select from the available cities listed above.\n")
                    
                    retry_count += 1
                    if retry_count < self.max_retries:
                        print(f"Attempts remaining: {self.max_retries - retry_count}\n")
                        # Show cities again if user wants to retry
                        self._display_available_cities()
            
            except KeyboardInterrupt:
                print("\n\nInput cancelled by user.")
                return None
            except EOFError:
                print("\n\nEnd of input reached.")
                return None
            except Exception as e:
                logger.error(f"Error collecting city input: {str(e)}")
                print(f"\nAn error occurred: {str(e)}\n")
                retry_count += 1
        
        print(f"\nMaximum retry attempts ({self.max_retries}) reached. Please try again later.\n")
        return None
    
    def collect_price_range(self) -> Optional[PriceRange]:
        """
        Collect and validate price range input from user
        
        Returns:
            Validated PriceRange enum or None if user cancels
        """
        retry_count = 0
        
        # Display price range options
        self._display_price_options()
        
        while retry_count < self.max_retries:
            try:
                print("Select price range (enter number or name): ", end="", flush=True)
                price_input = input().strip()
                
                if not price_input:
                    print("Price range selection is required. Please try again.\n")
                    retry_count += 1
                    continue
                
                # Validate price range
                is_valid, price_range, error_msg = self.validator.validate_price_range(price_input)
                
                if is_valid:
                    print(f"✓ Price range selected: {price_range.value}\n")
                    return price_range
                else:
                    print(f"\n{error_msg}\n")
                    retry_count += 1
                    if retry_count < self.max_retries:
                        print(f"Attempts remaining: {self.max_retries - retry_count}\n")
                        self._display_price_options()
            
            except KeyboardInterrupt:
                print("\n\nInput cancelled by user.")
                return None
            except EOFError:
                print("\n\nEnd of input reached.")
                return None
            except Exception as e:
                logger.error(f"Error collecting price range input: {str(e)}")
                print(f"\nAn error occurred: {str(e)}\n")
                retry_count += 1
        
        print(f"\nMaximum retry attempts ({self.max_retries}) reached. Please try again later.\n")
        return None
    
    def _display_available_cities(self) -> None:
        """Display available cities to the user"""
        cities = self.validator.get_available_cities()
        
        if not cities:
            print("Note: No cities available in dataset.\n")
            return
        
        print("\nAvailable cities:")
        # Display cities in columns for better readability
        if len(cities) <= 10:
            # Show all cities if 10 or fewer
            for i, city in enumerate(cities, 1):
                print(f"  {i}. {city}")
        else:
            # Show first 15 cities, then indicate more
            for i, city in enumerate(cities[:15], 1):
                print(f"  {i}. {city}")
            if len(cities) > 15:
                print(f"  ... and {len(cities) - 15} more cities")
        print()
    
    def _display_price_options(self) -> None:
        """Display available price range options"""
        options = self.validator.get_price_range_options()
        print("\nAvailable price ranges:")
        for option in options:
            print(f"  {option['number']}. {option['value']} - {option['description']}")
        print()
    
    def collect_user_input(self) -> Optional[Dict[str, any]]:
        """
        Collect complete user input (city and price range)
        
        Returns:
            Dictionary with 'city' and 'price_range' keys, or None if cancelled
        """
        self.display_welcome()
        
        # Collect city
        city = self.collect_city()
        if city is None:
            return None
        
        # Collect price range
        price_range = self.collect_price_range()
        if price_range is None:
            return None
        
        # Confirm selection
        print("\n" + "-" * 60)
        print("Selection Summary:")
        print(f"  City: {city}")
        print(f"  Price Range: {price_range.value}")
        print("-" * 60)
        
        # Ask for confirmation
        try:
            print("\nProceed with this selection? (y/n): ", end="", flush=True)
            confirmation = input().strip().lower()
            
            if confirmation in ['y', 'yes']:
                print("\n✓ Processing your request...\n")
                return {
                    'city': city,
                    'price_range': price_range
                }
            else:
                print("\nSelection cancelled. You can start over.\n")
                return None
        
        except KeyboardInterrupt:
            print("\n\nInput cancelled by user.")
            return None
        except EOFError:
            print("\n\nEnd of input reached.")
            return None
    
    def display_processing(self) -> None:
        """Display processing message"""
        print("Processing your request...")
        print("This may take a few moments.\n")
    
    def display_error(self, message: str) -> None:
        """
        Display error message
        
        Args:
            message: Error message to display
        """
        print(f"\n❌ Error: {message}\n")
    
    def prompt_continue(self) -> bool:
        """
        Prompt user if they want to continue with another query
        
        Returns:
            True if user wants to continue, False otherwise
        """
        try:
            print("\nWould you like to search again? (y/n): ", end="", flush=True)
            response = input().strip().lower()
            return response in ['y', 'yes']
        except (KeyboardInterrupt, EOFError):
            return False
    
    def display_goodbye(self) -> None:
        """Display goodbye message"""
        print("\n" + "=" * 60)
        print("Thank you for using Zomato AI Restaurant Recommendation Service!")
        print("=" * 60 + "\n")
