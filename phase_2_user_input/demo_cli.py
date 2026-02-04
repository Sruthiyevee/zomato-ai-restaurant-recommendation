"""
Demo script showing CLI output without requiring user input
This demonstrates what the CLI looks like
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from validator import InputValidator, PriceRange
from cli_handler import CLIHandler
from session_manager import SessionManager


def demo_cli_output():
    """Demonstrate CLI output"""
    print("\n" + "=" * 60)
    print("  CLI INTERFACE DEMONSTRATION")
    print("=" * 60)
    print("\nThis shows what the CLI interface looks like.\n")
    
    # Initialize with sample cities
    available_cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
        'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat'
    ]
    
    validator = InputValidator(available_cities=available_cities)
    cli_handler = CLIHandler(validator=validator)
    session_manager = SessionManager()
    
    # Show welcome message
    print("\n" + "-" * 60)
    print("WELCOME MESSAGE:")
    print("-" * 60)
    cli_handler.display_welcome()
    
    # Show price range options
    print("\n" + "-" * 60)
    print("PRICE RANGE OPTIONS DISPLAY:")
    print("-" * 60)
    cli_handler._display_price_options()
    
    # Demonstrate validation
    print("\n" + "-" * 60)
    print("VALIDATION EXAMPLES:")
    print("-" * 60)
    
    # Valid city
    is_valid, normalized, suggestions = validator.validate_city("Mumbai")
    print(f"Input: 'Mumbai'")
    print(f"  Valid: {is_valid}, Normalized: {normalized}")
    
    # Invalid city with suggestions
    is_valid, normalized, suggestions = validator.validate_city("Mumbay")
    print(f"\nInput: 'Mumbay' (typo)")
    print(f"  Valid: {is_valid}")
    if suggestions:
        print(f"  Suggestions: {', '.join(suggestions)}")
    
    # Valid price range
    is_valid, price_range, error = validator.validate_price_range("1")
    print(f"\nInput: '1' (price range)")
    print(f"  Valid: {is_valid}, Price Range: {price_range.value if price_range else None}")
    
    is_valid, price_range, error = validator.validate_price_range("Budget")
    print(f"\nInput: 'Budget' (price range)")
    print(f"  Valid: {is_valid}, Price Range: {price_range.value if price_range else None}")
    
    # Invalid price range
    is_valid, price_range, error = validator.validate_price_range("5")
    print(f"\nInput: '5' (invalid price range)")
    print(f"  Valid: {is_valid}, Error: {error}")
    
    # Show session management
    print("\n" + "-" * 60)
    print("SESSION MANAGEMENT:")
    print("-" * 60)
    print(f"Session ID: {session_manager.session_id}")
    print(f"Initial State: {session_manager.state.value}")
    
    # Simulate setting input
    session_manager.set_user_input("Delhi", PriceRange.MID_RANGE)
    print(f"After setting input - State: {session_manager.state.value}")
    print(f"Current City: {session_manager.current_city}")
    print(f"Current Price Range: {session_manager.current_price_range.value}")
    
    # Show session info
    print("\n" + "-" * 60)
    print("SESSION INFO:")
    print("-" * 60)
    session_info = session_manager.get_session_info()
    for key, value in session_info.items():
        print(f"  {key}: {value}")
    
    # Show goodbye message
    print("\n" + "-" * 60)
    print("GOODBYE MESSAGE:")
    print("-" * 60)
    cli_handler.display_goodbye()
    
    print("\n" + "=" * 60)
    print("To test the interactive CLI, run: python test_cli.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    demo_cli_output()
