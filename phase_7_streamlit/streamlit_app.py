import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="Zomato AI Restaurant Recommendation",
    page_icon="🍽️",
    layout="wide"
)

# Load Environment Variables
# We need to load from phase_4_recommendation/.env
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
ENV_PATH = os.path.join(PROJECT_ROOT, 'phase_4_recommendation', '.env')

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    st.warning("Environment file (.env) not found in phase_4_recommendation. Application might not work correctly.")

# Add Component Source Paths
PHASE_1_SRC = os.path.join(PROJECT_ROOT, 'phase_1_data_ingestion', 'src')
PHASE_4_SRC = os.path.join(PROJECT_ROOT, 'phase_4_recommendation', 'src')

if PHASE_1_SRC not in sys.path:
    sys.path.append(PHASE_1_SRC)
if PHASE_4_SRC not in sys.path:
    sys.path.append(PHASE_4_SRC)

# Import Core Components
try:
    from storage import ZomatoDataStorage
    from recommendation_engine import RecommendationEngine
except ImportError as e:
    st.error(f"Failed to import core components: {e}")
    st.stop()

# Initialize Global Components
@st.cache_resource
def get_engine():
    return RecommendationEngine()

@st.cache_resource
def get_storage():
    return ZomatoDataStorage()

@st.cache_data
def load_data():
    storage = get_storage()
    try:
        df = storage.load_from_db()
        if df.empty:
            return None, "Database is empty."
        
        # Transform data for the engine
        restaurants = []
        for _, row in df.iterrows():
            restaurants.append({
                'name': row.get('restaurant_name') or 'Unknown',
                'cuisine': row.get('primary_cuisine') or 'Unknown',
                'rating': float(row.get('normalized_rating') or 0.0),
                'review_count': int(row.get('review_count') or 0),
                'price_range': row.get('price_range') or 'Unknown',
                'composite_score': float(row.get('composite_score') or 0.0),
                'key_features': str(row.get('cuisine_list', '')),
                'city': row.get('city') or 'Unknown'
            })
        return restaurants, None
    except Exception as e:
        return None, str(e)

# --- UI Layout ---

st.title("🍽️ Zomato AI Restaurant Recommendation")
st.markdown("Find the best restaurants tailored to your preferences using AI.")

# Sidebar for Filters
with st.sidebar:
    st.header("Preferences")
    
    # Load Data
    restaurants_data, error = load_data()
    
    if error:
        st.error(f"Data Error: {error}")
        st.stop()
        
    if not restaurants_data:
        st.warning("No restaurant data available.")
        st.stop()
        
    # City Selection
    cities = sorted(list(set(r.get('city', 'Unknown') for r in restaurants_data)))
    selected_city = st.selectbox("Select City", cities)
    
    # Price Range Selection
    # Extract available price ranges or hardcode common ones
    # available_prices = sorted(list(set(r.get('price_range', 'Unknown') for r in restaurants_data)))
    # For better UX, let's use standard ranges but verifying against data is good practice.
    # We will use hardcoded for better UI consistency as per Main.py
    price_ranges = ["Budget", "Mid-Range", "Premium", "Luxury"]
    selected_price = st.selectbox("Price Range", price_ranges)
    
    generate_btn = st.button("Generate Recommendations", type="primary")

# Main Content Area
if generate_btn:
    engine = get_engine()
    
    with st.spinner(f"Finding the best {selected_price} restaurants in {selected_city}..."):
        try:
            success, recommendations, error_msg = engine.generate_recommendations(
                restaurants=restaurants_data,
                city=selected_city,
                price_range=selected_price,
                max_recommendations=5
            )
            
            if success:
                st.success(f"Found {len(recommendations)} recommendations!")
                
                for i, rec in enumerate(recommendations, 1):
                    with st.container():
                        # Card-like layout
                        col1, col2 = st.columns([1, 4])
                        
                        with col1:
                            st.metric(label="Rating", value=f"{rec.get('rating', 'N/A'):.1f}⭐")
                            st.caption(f"Rank #{rec.get('rank', i)}")
                            
                        with col2:
                            st.subheader(rec.get('restaurant_name', 'Unknown Restaurant'))
                            st.markdown(f"**Cuisine:** {rec.get('cuisine', 'Unknown')}")
                            st.markdown(f"**Price:** {rec.get('price_range', 'Unknown')}")
                            
                            reasoning = rec.get('reasoning') or rec.get('key_highlights')
                            if reasoning:
                                st.info(f"Why this? {reasoning}")
                                
                        st.divider()
            else:
                st.error(f"Could not generate recommendations: {error_msg}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

else:
    # Initial State / Instructions
    st.info("👈 Select your city and price preference in the sidebar to get started!")
    
    # Show some stats or generic info
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Restaurants", len(restaurants_data))
    col2.metric("Cities Covered", len(cities))
    col3.metric("AI Engine", "Active")
