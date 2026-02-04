"""
Non-interactive demo showing CLI interface structure
This shows what the CLI looks like without requiring user input
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from validator import InputValidator, PriceRange
from cli_handler import CLIHandler
from session_manager import SessionManager


def show_cli_demo():
    """Show CLI demo output"""
    print("\n" + "=" * 70)
    print("  CLI INTERFACE DEMONSTRATION - Phase 2")
    print("=" * 70)
    
    # Initialize components
    available_cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
        'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat',
        'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane'
    ]
    
    validator = InputValidator(available_cities=available_cities)
    cli_handler = CLIHandler(validator=validator)
    session_manager = SessionManager()
    
    print("\n" + "-" * 70)
    print("STEP 1: WELCOME MESSAGE")
    print("-" * 70)
    cli_handler.display_welcome()
    
    print("\n" + "-" * 70)
    print("STEP 2: CITY INPUT PROMPT")
    print("-" * 70)
    print("Enter city name: ", end="")
    print("[USER WOULD TYPE HERE - e.g., 'Mumbai']")
    
    # Simulate valid city input
    print("\n✓ City selected: Mumbai")
    
    print("\n" + "-" * 70)
    print("STEP 3: PRICE RANGE OPTIONS")
    print("-" * 70)
    cli_handler._display_price_options()
    
    print("\n" + "-" * 70)
    print("STEP 4: PRICE RANGE INPUT PROMPT")
    print("-" * 70)
    print("Select price range (enter number or name): ", end="")
    print("[USER WOULD TYPE HERE - e.g., '2' or 'Mid-Range']")
    
    # Simulate valid price range input
    print("\n✓ Price range selected: Mid-Range")
    
    print("\n" + "-" * 70)
    print("STEP 5: CONFIRMATION")
    print("-" * 70)
    print("\n" + "-" * 60)
    print("Selection Summary:")
    print("  City: Mumbai")
    print("  Price Range: Mid-Range")
    print("-" * 60)
    print("\nProceed with this selection? (y/n): ", end="")
    print("[USER WOULD TYPE 'y' or 'n']")
    
    print("\n✓ Processing your request...")
    
    # Show session management
    print("\n" + "-" * 70)
    print("STEP 6: SESSION MANAGEMENT")
    print("-" * 70)
    session_manager.set_user_input("Mumbai", PriceRange.MID_RANGE)
    session_info = session_manager.get_session_info()
    
    print(f"\nSession Information:")
    print(f"  Session ID: {session_info['session_id']}")
    print(f"  State: {session_info['state']}")
    print(f"  City: {session_info['current_city']}")
    print(f"  Price Range: {session_info['current_price_range']}")
    print(f"  Query Count: {session_info['query_count']}")
    
    # Show error handling examples
    print("\n" + "-" * 70)
    print("ERROR HANDLING EXAMPLES")
    print("-" * 70)
    
    print("\nExample 1: Invalid City Input")
    print("Enter city name: [USER TYPES: 'Mumbay']")
    print("\nCity 'Mumbay' not found. Did you mean:")
    print("  1. Mumbai")
    print("\nAttempts remaining: 2")
    
    print("\nExample 2: Invalid Price Range")
    print("Select price range (enter number or name): [USER TYPES: '5']")
    print("\nInvalid price range. Valid options: 1. Budget, 2. Mid-Range, 3. Premium, 4. Luxury")
    print("\nAttempts remaining: 2")
    
    # Show validation examples
    print("\n" + "-" * 70)
    print("VALIDATION EXAMPLES")
    print("-" * 70)
    
    test_cases = [
        ("Mumbai", "Valid city - exact match"),
        ("mumbai", "Valid city - case insensitive"),
        ("Mumbay", "Invalid city - typo (will suggest 'Mumbai')"),
        ("1", "Valid price - numeric (Budget)"),
        ("Budget", "Valid price - text"),
        ("mid-range", "Valid price - text with hyphen"),
        ("5", "Invalid price - out of range"),
    ]
    
    for input_val, description in test_cases:
        if 'city' in description.lower():
            is_valid, normalized, suggestions = validator.validate_city(input_val)
            print(f"\nInput: '{input_val}' - {description}")
            if is_valid:
                print(f"  ✓ Valid: {normalized}")
            else:
                print(f"  ✗ Invalid")
                if suggestions:
                    print(f"  Suggestions: {', '.join(suggestions)}")
        else:
            is_valid, price_range, error = validator.validate_price_range(input_val)
            print(f"\nInput: '{input_val}' - {description}")
            if is_valid:
                print(f"  ✓ Valid: {price_range.value}")
            else:
                print(f"  ✗ Invalid: {error}")
    
    print("\n" + "-" * 70)
    print("GOODBYE MESSAGE")
    print("-" * 70)
    cli_handler.display_goodbye()
    
    print("\n" + "=" * 70)
    print("To test interactively, ensure Python is installed and run:")
    print("  python phase_2_user_input/test_cli.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    show_cli_demo()
