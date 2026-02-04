"""
Test script to demonstrate and test the CLI interface
Run this script to interact with the Phase 2 CLI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from validator import InputValidator, PriceRange
from cli_handler import CLIHandler
from session_manager import SessionManager, SessionState


def main():
    """Main function to test CLI"""
    print("\n" + "=" * 60)
    print("  PHASE 2 CLI TEST SCRIPT")
    print("=" * 60)
    print("\nThis script will test the CLI interface for user input collection.")
    print("You can interact with it to test city and price range inputs.\n")
    
    # Example available cities (in real app, these come from Phase 1 database)
    available_cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
        'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat',
        'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane'
    ]
    
    # Initialize components
    print("Initializing components...")
    validator = InputValidator(available_cities=available_cities)
    cli_handler = CLIHandler(validator=validator)
    session_manager = SessionManager()
    
    print(f"✓ Validator initialized with {len(available_cities)} cities")
    print(f"✓ CLI Handler initialized")
    print(f"✓ Session Manager initialized (Session ID: {session_manager.session_id})")
    
    # Test the CLI
    print("\n" + "-" * 60)
    print("Starting CLI interaction...")
    print("-" * 60 + "\n")
    
    try:
        # Collect user input through CLI
        user_input = cli_handler.collect_user_input()
        
        if user_input:
            print("\n" + "=" * 60)
            print("INPUT COLLECTION SUCCESSFUL")
            print("=" * 60)
            
            # Store in session
            session_manager.set_user_input(
                user_input['city'],
                user_input['price_range']
            )
            
            # Display session information
            print("\nSession Information:")
            session_info = session_manager.get_session_info()
            print(f"  Session ID: {session_info['session_id']}")
            print(f"  State: {session_info['state']}")
            print(f"  City: {session_info['current_city']}")
            print(f"  Price Range: {session_info['current_price_range']}")
            print(f"  Query Count: {session_info['query_count']}")
            
            # Simulate processing
            print("\n" + "-" * 60)
            print("Simulating processing...")
            print("-" * 60)
            session_manager.start_processing()
            print(f"Session state: {session_manager.state.value}")
            
            # Simulate completion
            mock_results = {
                'recommendations': [
                    {'name': 'Restaurant A', 'rating': 4.5},
                    {'name': 'Restaurant B', 'rating': 4.2}
                ]
            }
            session_manager.complete_query(mock_results)
            print(f"Session state: {session_manager.state.value}")
            print(f"Query history entries: {len(session_manager.get_query_history())}")
            
            # Ask if user wants to continue
            print("\n" + "-" * 60)
            if cli_handler.prompt_continue():
                print("\nResetting for new query...")
                session_manager.reset_for_new_query()
                print(f"Session state: {session_manager.state.value}")
                print("You can run this script again to test another query.")
            else:
                cli_handler.display_goodbye()
        else:
            print("\n" + "=" * 60)
            print("INPUT COLLECTION CANCELLED")
            print("=" * 60)
            print("\nUser cancelled the input collection process.")
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("TEST INTERRUPTED BY USER")
        print("=" * 60)
        cli_handler.display_goodbye()
    except Exception as e:
        print(f"\n❌ Error during CLI test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
