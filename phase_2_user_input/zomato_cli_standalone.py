"""
Standalone CLI application for Zomato Restaurant Recommendation
This version is optimized for building into an executable
"""

import sys
import os
from pathlib import Path

# Add src to path - handle both script and executable modes
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = sys._MEIPASS
    src_path = os.path.join(base_path, 'src')
else:
    # Running as script
    base_path = Path(__file__).parent
    src_path = base_path / "src"

sys.path.insert(0, str(src_path))

try:
    from validator import InputValidator, PriceRange
    from cli_handler import CLIHandler
    from session_manager import SessionManager, SessionState
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Looking in: {src_path}")
    sys.exit(1)


def main():
    """Main function for CLI application"""
    print("\n" + "=" * 60)
    print("  ZOMATO AI RESTAURANT RECOMMENDATION SERVICE")
    print("=" * 60)
    print("\nWelcome! I'll help you find the perfect restaurant.")
    print("Please provide the following information.\n")
    
    # Example available cities (in real app, these come from Phase 1 database)
    available_cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
        'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat',
        'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane'
    ]
    
    # Initialize components
    try:
        validator = InputValidator(available_cities=available_cities)
        cli_handler = CLIHandler(validator=validator)
        session_manager = SessionManager()
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        input("\nPress Enter to exit...")
        return
    
    # Main interaction loop
    while True:
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
                print(f"  City: {session_info['current_city']}")
                print(f"  Price Range: {session_info['current_price_range']}")
                
                # Simulate processing
                print("\n" + "-" * 60)
                print("Processing your request...")
                print("(In full application, this would call Phase 3 & 4)")
                print("-" * 60)
                
                session_manager.start_processing()
                
                # Simulate completion
                mock_results = {
                    'recommendations': [
                        {'name': 'Restaurant A', 'rating': 4.5},
                        {'name': 'Restaurant B', 'rating': 4.2}
                    ]
                }
                session_manager.complete_query(mock_results)
                
                print(f"\n✓ Query completed. Session state: {session_manager.state.value}")
                
                # Ask if user wants to continue
                print("\n" + "-" * 60)
                if cli_handler.prompt_continue():
                    print("\nResetting for new query...\n")
                    session_manager.reset_for_new_query()
                    continue
                else:
                    cli_handler.display_goodbye()
                    break
            else:
                print("\n" + "=" * 60)
                print("INPUT COLLECTION CANCELLED")
                print("=" * 60)
                
                if cli_handler.prompt_continue():
                    continue
                else:
                    cli_handler.display_goodbye()
                    break
        
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("INTERRUPTED BY USER")
            print("=" * 60)
            cli_handler.display_goodbye()
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            if not cli_handler.prompt_continue():
                break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
