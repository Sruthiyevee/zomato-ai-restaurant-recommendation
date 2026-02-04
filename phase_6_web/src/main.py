import sys
import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Environment Variables
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
ENV_PATH = os.path.join(PROJECT_ROOT, 'phase_4_recommendation', '.env')
load_dotenv(ENV_PATH)

sys.path.append(PROJECT_ROOT)



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
    logger.error(f"Failed to import core components: {e}")
    sys.exit(1)

# Initialize App
app = FastAPI(title="Zomato AI Recommendation Service")

# Mount Static Files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Templates
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# Models
class RecommendationRequest(BaseModel):
    city: str
    price_range: str

# Global State
restaurants_data: List[Dict] = []
engine = RecommendationEngine()
storage = ZomatoDataStorage()

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    global restaurants_data
    logger.info("Loading restaurant data from database...")
    try:
        df = storage.load_from_db()
        if not df.empty:
            # Transform to format expected by Recommendation Engine
            for _, row in df.iterrows():
                restaurants_data.append({
                    'name': row.get('restaurant_name') or 'Unknown',
                    'cuisine': row.get('primary_cuisine') or 'Unknown',
                    'rating': float(row.get('normalized_rating') or 0.0),
                    'review_count': int(row.get('review_count') or 0),
                    'price_range': row.get('price_range') or 'Unknown',
                    'composite_score': float(row.get('composite_score') or 0.0),
                    'key_features': str(row.get('cuisine_list', ''))
                })
            logger.info(f"Loaded {len(restaurants_data)} restaurants from DB.")
        else:
            logger.warning("Database empty. Recommendations will not work.")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/v1/cities")
async def get_cities():
    """Get list of unique cities"""
    if not restaurants_data:
        return {"cities": []}
    
    # Extract unique cities from loaded data (we can also query DB directly, but this is cached in memory)
    # Using a set for uniqueness
    # In a real heavy app, query DB. Here, we already loaded all into memory for the Engine.
    cities = sorted(list(set(r.get('city', '') for r in restaurants_data if r.get('city'))))
    
    # If city info wasn't in the transformation above, we might need to fetch it differently or add it.
    # Ah, I missed adding 'city' to the restaurants_data list in startup_event.
    # Let me fix that logic in the same step if I can, or rely on DB.
    
    # Actually, let's query the DB for cities efficiently
    try:
        # Re-using storage connection for specific query
        df = storage.load_from_db("SELECT DISTINCT city FROM restaurants ORDER BY city")
        cities = df['city'].tolist()
        return {"cities": cities}
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        return {"cities": [], "error": str(e)}

@app.get("/api/v1/prices")
async def get_prices():
    """Get available price ranges"""
    return {"prices": ["Budget", "Mid-Range", "Premium", "Luxury"]}

@app.post("/api/v1/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Generate recommendations using LLM"""
    if not restaurants_data:
        raise HTTPException(status_code=503, detail="Restaurant data not loaded")
        
    try:
        success, recommendations, error = engine.generate_recommendations(
            restaurants=restaurants_data,
            city=request.city,
            price_range=request.price_range,
            max_recommendations=5
        )
        
        if success:
            return {"success": True, "recommendations": recommendations, "count": len(recommendations)}
        else:
            return {"success": False, "error": error}
            
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
