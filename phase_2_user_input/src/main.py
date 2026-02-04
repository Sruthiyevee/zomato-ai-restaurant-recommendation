"""
Main entry point for Phase 2 User Input
Example usage of the Phase 2 components
"""

from validator import InputValidator, PriceRange
from cli_handler import CLIHandler
from session_manager import SessionManager, SessionState


def main():
    """Example usage of Phase 2 components"""
    # Example: Initialize with available cities from dataset
    # In real usage, these would come from Phase 1 database
    available_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
    
    # Initialize components
    validator = InputValidator(available_cities=available_cities)
    cli_handler = CLIHandler(validator=validator)
    session_manager = SessionManager()
    
    # Collect user input
    user_input = cli_handler.collect_user_input()
    
    if user_input:
        # Store in session
        session_manager.set_user_input(
            user_input['city'],
            user_input['price_range']
        )
        
        # Display session info
        session_info = session_manager.get_session_info()
        print(f"\nSession ID: {session_info['session_id']}")
        print(f"City: {session_info['current_city']}")
        print(f"Price Range: {session_info['current_price_range']}")
        
        # Ready for Phase 3 integration
        return user_input
    else:
        print("\nUser input collection cancelled.")
        return None


if __name__ == "__main__":
    main()
