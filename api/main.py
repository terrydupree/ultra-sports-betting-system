"""
FastAPI Main Application for Ultra Sports Betting System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sports.mlb.mlb_analyzer import MLBAnalyzer
from sports.nfl.nfl_analyzer import NFLAnalyzer
from core.utils.logger import get_logger

# Initialize FastAPI app
app = FastAPI(
    title="Ultra Sports Betting System API",
    description="Comprehensive multi-sport betting analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logger
logger = get_logger("main_api")

# Initialize analyzers
mlb_analyzer = MLBAnalyzer()
nfl_analyzer = NFLAnalyzer()

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Ultra Sports Betting System API",
        "version": "1.0.0",
        "sports_supported": ["mlb", "nfl", "nba", "nhl", "soccer", "tennis", "golf", "mma"],
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "running",
                "mlb_analyzer": "initialized",
                "nfl_analyzer": "initialized"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.get("/api/mlb/games")
async def get_mlb_games(date: Optional[str] = None):
    """Get MLB games for a specific date."""
    try:
        games_data = mlb_analyzer.fetch_game_data(date)
        
        if games_data.empty:
            return {"games": [], "count": 0, "date": date or "today"}
        
        # Convert DataFrame to list of dictionaries
        games_list = games_data.to_dict('records')
        
        return {
            "games": games_list,
            "count": len(games_list),
            "date": date or "today",
            "sport": "mlb"
        }
        
    except Exception as e:
        logger.error(f"Error fetching MLB games: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nfl/games")
async def get_nfl_games(date: Optional[str] = None):
    """Get NFL games for a specific date."""
    try:
        games_data = nfl_analyzer.fetch_game_data(date)
        
        if games_data.empty:
            return {"games": [], "count": 0, "date": date or "today"}
        
        # Convert DataFrame to list of dictionaries
        games_list = games_data.to_dict('records')
        
        return {
            "games": games_list,
            "count": len(games_list),
            "date": date or "today",
            "sport": "nfl"
        }
        
    except Exception as e:
        logger.error(f"Error fetching NFL games: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mlb/teams/{team_id}/stats")
async def get_mlb_team_stats(team_id: str):
    """Get MLB team statistics."""
    try:
        stats = mlb_analyzer.calculate_team_stats(team_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "team_stats": stats,
            "sport": "mlb",
            "team_id": team_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching MLB team stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nfl/teams/{team_id}/stats")
async def get_nfl_team_stats(team_id: str):
    """Get NFL team statistics."""
    try:
        stats = nfl_analyzer.calculate_team_stats(team_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "team_stats": stats,
            "sport": "nfl",
            "team_id": team_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching NFL team stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mlb/predict")
async def predict_mlb_game(game_data: Dict):
    """Predict MLB game outcome."""
    try:
        prediction = mlb_analyzer.predict_game_outcome(game_data)
        
        if "error" in prediction:
            raise HTTPException(status_code=400, detail=prediction["error"])
        
        return {
            "prediction": prediction,
            "sport": "mlb"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting MLB game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/nfl/predict")
async def predict_nfl_game(game_data: Dict):
    """Predict NFL game outcome."""
    try:
        prediction = nfl_analyzer.predict_game_outcome(game_data)
        
        if "error" in prediction:
            raise HTTPException(status_code=400, detail=prediction["error"])
        
        return {
            "prediction": prediction,
            "sport": "nfl"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting NFL game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mlb/recommendations")
async def get_mlb_recommendations(game_data: Dict, odds_data: Dict):
    """Get MLB betting recommendations."""
    try:
        recommendations = mlb_analyzer.get_betting_recommendations(game_data, odds_data)
        
        return {
            "recommendations": recommendations,
            "sport": "mlb",
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error getting MLB recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/nfl/recommendations")
async def get_nfl_recommendations(game_data: Dict, odds_data: Dict):
    """Get NFL betting recommendations."""
    try:
        recommendations = nfl_analyzer.get_betting_recommendations(game_data, odds_data)
        
        return {
            "recommendations": recommendations,
            "sport": "nfl",
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error getting NFL recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sports")
async def get_supported_sports():
    """Get list of supported sports."""
    return {
        "sports": [
            {
                "key": "mlb",
                "name": "Major League Baseball",
                "season": "April-October",
                "status": "active"
            },
            {
                "key": "nfl", 
                "name": "National Football League",
                "season": "September-February",
                "status": "active"
            },
            {
                "key": "nba",
                "name": "National Basketball Association",
                "season": "October-June", 
                "status": "coming_soon"
            },
            {
                "key": "nhl",
                "name": "National Hockey League",
                "season": "October-June",
                "status": "coming_soon"
            },
            {
                "key": "soccer",
                "name": "Soccer",
                "season": "Year-round",
                "status": "coming_soon"
            },
            {
                "key": "tennis",
                "name": "Tennis",
                "season": "Year-round",
                "status": "coming_soon"
            },
            {
                "key": "golf",
                "name": "Golf",
                "season": "Year-round",
                "status": "coming_soon"
            },
            {
                "key": "mma",
                "name": "Mixed Martial Arts",
                "season": "Year-round",
                "status": "coming_soon"
            }
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)