import sys
import os
import time
from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_ROOT)

from phase_6_web.src.main import app

def run_verification():
    print("Initializing Test Client...")
    
    test_cases = [
        {"city": "Bangalore", "price_range": "Mid-Range"},
        {"city": "New Delhi", "price_range": "Luxury"},
        {"city": "Pune", "price_range": "Budget"}
    ]
    
    print(f"\nRunning {len(test_cases)} Live API Calls...")
    print("=" * 60)
    
    # Use TestClient as context manager to trigger startup events (loading data)
    with TestClient(app) as client:
        for i, case in enumerate(test_cases, 1):
            print(f"\n[Call {i}] Requesting recommendations for {case['city']} ({case['price_range']})...")
            start_time = time.time()
            
            try:
                response = client.post(
                    "/api/v1/recommendations", 
                    json=case
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        execution_time = f"{duration:.2f}s"
                        recs = data.get("recommendations", [])
                        print(f"Nodes: {app.url_path_for('get_recommendations')} returned 200 OK")
                        print(f"Status: SUCCESS ({execution_time})")
                        print(f"Received {len(recs)} recommendations.")
                        if recs:
                            top_pick = recs[0]
                            print(f"Top Pick: {top_pick.get('restaurant_name')} - {top_pick.get('rating')} Stars")
                            print(f"Reason: {top_pick.get('reasoning')[:100]}...")
                    else:
                        print("Status: FAILED (API returned success=False)")
                        print(f"Error: {data.get('error')}")
                else:
                    print(f"Status: FAILED (HTTP {response.status_code})")
                    print(f"Detail: {response.text}")
                    
            except Exception as e:
                print(f"Status: ERROR (Exception occurred)")
                print(f"Details: {e}")
            
            print("-" * 60)

if __name__ == "__main__":
    run_verification()
