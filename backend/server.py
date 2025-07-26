from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import httpx
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Radio Browser API Base URL  
RADIO_BROWSER_BASE = "https://www.radio-browser.info/webservice"

# Models
class RadioStation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stationuuid: str
    name: str
    url: str
    homepage: Optional[str] = ""
    favicon: Optional[str] = ""
    country: Optional[str] = ""
    countrycode: Optional[str] = ""
    state: Optional[str] = ""
    language: Optional[str] = ""
    tags: Optional[str] = ""
    bitrate: Optional[int] = 0
    codec: Optional[str] = ""
    votes: Optional[int] = 0

class FavoriteStation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"  # For MVP, using single user
    station_uuid: str
    station_name: str
    station_url: str
    country: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SearchQuery(BaseModel):
    query: Optional[str] = ""
    country: Optional[str] = ""
    limit: Optional[int] = 50

# Radio Browser API Integration
async def fetch_radio_stations(limit: int = 50, country: str = "", name: str = ""):
    """Fetch radio stations from Radio Browser API"""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            if country:
                url = f"{RADIO_BROWSER_BASE}/json/stations/bycountry/{country}"
            elif name:
                url = f"{RADIO_BROWSER_BASE}/json/stations/search?name={name}&limit={limit}"
            else:
                url = f"{RADIO_BROWSER_BASE}/json/stations/topvote/{limit}"
            
            response = await client.get(url)
            response.raise_for_status()
            
            stations_data = response.json()
            stations = []
            
            for station in stations_data[:limit]:
                stations.append(RadioStation(
                    stationuuid=station.get('stationuuid', ''),
                    name=station.get('name', 'Unknown Station'),
                    url=station.get('url', ''),
                    homepage=station.get('homepage', ''),
                    favicon=station.get('favicon', ''),
                    country=station.get('country', ''),
                    countrycode=station.get('countrycode', ''),
                    state=station.get('state', ''),
                    language=station.get('language', ''),
                    tags=station.get('tags', ''),
                    bitrate=station.get('bitrate', 0),
                    codec=station.get('codec', ''),
                    votes=station.get('votes', 0)
                ))
            
            return stations
    except Exception as e:
        logger.error(f"Error fetching radio stations: {e}")
        return []

async def fetch_countries():
    """Fetch list of countries from Radio Browser API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{RADIO_BROWSER_BASE}/json/countries"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        return []

# API Routes
@api_router.get("/")
async def root():
    return {"message": "World Radio API - Listen to radios from around the globe!"}

@api_router.get("/stations", response_model=List[RadioStation])
async def get_stations(limit: int = 50, country: str = "", name: str = ""):
    """Get radio stations with optional filters"""
    stations = await fetch_radio_stations(limit=limit, country=country, name=name)
    return stations

@api_router.get("/countries")
async def get_countries():
    """Get list of available countries"""
    countries = await fetch_countries()
    return countries

@api_router.post("/search", response_model=List[RadioStation])
async def search_stations(search_query: SearchQuery):
    """Search radio stations"""
    stations = await fetch_radio_stations(
        limit=search_query.limit,
        country=search_query.country,
        name=search_query.query
    )
    return stations

@api_router.post("/favorites", response_model=FavoriteStation)
async def add_favorite(station: FavoriteStation):
    """Add station to favorites"""
    try:
        # Check if already exists
        existing = await db.favorites.find_one({
            "station_uuid": station.station_uuid,
            "user_id": station.user_id
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Station already in favorites")
        
        favorite_dict = station.dict()
        await db.favorites.insert_one(favorite_dict)
        return station
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to add favorite")

@api_router.get("/favorites", response_model=List[FavoriteStation])
async def get_favorites(user_id: str = "default_user"):
    """Get user's favorite stations"""
    try:
        favorites = await db.favorites.find({"user_id": user_id}).to_list(1000)
        return [FavoriteStation(**fav) for fav in favorites]
    except Exception as e:
        logger.error(f"Error getting favorites: {e}")
        return []

@api_router.delete("/favorites/{station_uuid}")
async def remove_favorite(station_uuid: str, user_id: str = "default_user"):
    """Remove station from favorites"""
    try:
        result = await db.favorites.delete_one({
            "station_uuid": station_uuid,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        return {"message": "Favorite removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove favorite")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()