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
# Load Environment Variables & Paths
# -----------------------------------------------------------------------------
# Ensure we have the correct project root regardless of where streamlit is run
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(current_dir, '..'))

# Critical Paths
ENV_PATH = os.path.join(PROJECT_ROOT, 'phase_4_recommendation', '.env')
DB_PATH = os.path.join(PROJECT_ROOT, 'phase_1_data_ingestion', 'data', 'processed', 'zomato_restaurants.db')
PHASE_1_SRC = os.path.join(PROJECT_ROOT, 'phase_1_data_ingestion', 'src')
PHASE_4_SRC = os.path.join(PROJECT_ROOT, 'phase_4_recommendation', 'src')

# Add Source Paths to System Path
if PHASE_1_SRC not in sys.path:
    sys.path.append(PHASE_1_SRC)
if PHASE_4_SRC not in sys.path:
    sys.path.append(PHASE_4_SRC)

# Load .env explicitly
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    # Debugging: Uncomment to verify
    # st.write(f"Loaded .env from: {ENV_PATH}")
else:
    st.warning(f"⚠️ Environment file not found at: {ENV_PATH}")

# Import Core Components
try:
    from storage import ZomatoDataStorage
    from recommendation_engine import RecommendationEngine
    from groq_client import GroqClient
except ImportError as e:
    st.error(f"❌ Failed to import core components: {e}")
    st.code(f"Sys Path: {sys.path}", language="text")
    st.stop()

# --- Initialization Functions ---

@st.cache_resource
def get_engine(api_key: str = None):
    """
    Initialize the recommendation engine with the best available API key.
    Priority:
    1. Key provided in arguments (User Input)
    2. Key in Streamlit Secrets
    3. Key in Environment Variables (.env)
    """
    # Resolve API Key
    final_api_key = api_key
    
    if not final_api_key:
        # Check Secrets
        if "GROQ_API_KEY" in st.secrets:
            final_api_key = st.secrets["GROQ_API_KEY"]
        
    if not final_api_key:
        # Check Environment (loaded via dotenv)
        final_api_key = os.getenv("GROQ_API_KEY")
        
    # Initialize Engine
    try:
        if final_api_key:
            client = GroqClient(api_key=final_api_key)
            return RecommendationEngine(groq_client=client)
        else:
            # Fallback (might fail if env var is missing too, handled by Engine)
            return RecommendationEngine()
    except Exception as e:
        # Return None or raise to be handled by caller
        raise e

@st.cache_resource
def get_storage():
    """Initialize storage with absolute DB path"""
    return ZomatoDataStorage(db_path=DB_PATH)

@st.cache_data
def load_data():
    storage = get_storage()
    try:
        # Verify DB exists first
        if not os.path.exists(DB_PATH):
            return None, f"Database file not found at: {DB_PATH}"

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

# Sidebar for Preferences & Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. API Key Input
    # Check if we have a key from secrets or env to show status
    has_env_key = os.getenv("GROQ_API_KEY") is not None
    has_secret_key = "GROQ_API_KEY" in st.secrets
    
    api_key_input = st.text_input(
        "Groq API Key",
        type="password",
        help="Enter your Groq API Key here. Leave empty to use system defaults.",
        placeholder="gsk_..."
    )
    
    if not api_key_input and not has_env_key and not has_secret_key:
        st.warning("⚠️ No API Key found! Please enter one.")
    elif api_key_input:
        st.success("Key provided via input.")
    else:
        st.info("Using system/env key.")

    st.divider()
    
    st.header("🔎 Preferences")
    
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
    
    # Price Range
    price_ranges = ["Budget", "Mid-Range", "Premium", "Luxury"]
    selected_price = st.selectbox("Price Range", price_ranges)
    
    generate_btn = st.button("Generate Recommendations", type="primary")

# Main Content Area
if generate_btn:
    try:
        # Initialize engine with the user input key (if any)
        engine = get_engine(api_key=api_key_input)
        
        with st.spinner(f"Finding the best {selected_price} restaurants in {selected_city}..."):
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
