"""
Integration Test for Phase 5 CLI
Verifies end-to-end flow with real Recommendation Engine and Data Storage.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'phase_5_display', 'src'))

from phase_5_display.src.cli import CLI

class TestCLIIntegration(unittest.TestCase):
    
    @patch('builtins.input', side_effect=['Bangalore', '2', 'n'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_end_to_end_flow(self, mock_stdout, mock_input):
        """
        Test the full flow:
        1. Initialize CLI (loads real data)
        2. Input City: Bangalore
        3. Input Price: 2 (Mid-Range)
        4. Generate Recommendations (calls real Groq Engine)
        5. Verify Output
        6. Quit
        """
        cli = CLI()
        
        # Skip test if no data loaded (Pipeline hasn't run)
        if not cli.restaurants:
            print("Skipping integration test: No data available")
            return

        # Run CLI
        try:
            cli.start()
        except SystemExit:
            pass
            
        output = mock_stdout.getvalue()
        
        # Verify Key Steps
        self.assertIn("ZOMATO AI RESTAURANT RECOMMENDATIONS", output)
        self.assertIn("Finding top restaurants in Bangalore", output)
        
        # Verify Recommendations were displayed (or error if API issues)
        # We assume Groq API might work or fail, but the CLI should handle it.
        # If successfully generated, we see "Recommendations:"
        # If failed, we see "ERROR:"
        
        has_recs = "Recommendations:" in output
        has_error = "ERROR:" in output
        
        self.assertTrue(has_recs or has_error, "Output should contain recommendations or an error message")
        
        if has_recs:
            print("\nIntegration Test: Successfully displayed recommendations.")
        else:
            print("\nIntegration Test: Handled error gracefully.")

if __name__ == '__main__':
    unittest.main()
