"""
FastAPI application for job market demand forecasting.
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.config import settings
from backend.app.schemas import HealthResponse, ForecastResponse, SeriesResponse
from backend.app.services.forecast import forecast_service
from backend.app.services.data_store import data_store


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# CORS middleware for frontend
# Allow both local development and production (Render) URLs
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "https://job-prediction-llm.vercel.app",
    "https://jobpredictionllm.up.railway.app",
    "https://jobprediction-llm.up.railway.app",
]

# On Render, allow all origins for flexibility (or restrict to Vercel domain for security)
if os.getenv("RENDER"):
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.
    Use this endpoint for Render health checks and external pingers
    to prevent the service from going idle.
    """
    return {"ok": True}


@app.get("/ping")
async def ping():
    """
    Simple ping endpoint for keep-alive requests.
    Returns timestamp to verify service is active.
    """
    from datetime import datetime
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "service": "job-market-forecaster"
    }


@app.get("/series", response_model=SeriesResponse)
async def get_series(
    role: str = Query(..., description="Job role (e.g., 'Software Engineer')"),
    location: str = Query(..., description="Location (e.g., 'New York, NY')"),
    max_weeks: Optional[int] = Query(None, description="Maximum weeks to return (default: all)")
):
    """
    Get historical time series data for a role/location.
    """
    try:
        df = data_store.load_series(role, location, max_weeks=max_weeks or settings.MAX_HISTORY_WEEKS)
        points = data_store.to_time_series_points(df)
        
        return SeriesResponse(
            role=role,
            location=location,
            series=points
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    role: str = Query(..., description="Job role (e.g., 'Software Engineer')"),
    location: str = Query(..., description="Location (e.g., 'New York, NY')"),
    horizon: int = Query(settings.DEFAULT_HORIZON, ge=1, le=52, description="Forecast horizon in weeks")
):
    """
    Generate forecast for a role/location.
    
    Uses recursive forecasting with a 1-step ahead LSTM model.
    """
    try:
        result = forecast_service.forecast(role, location, horizon=horizon)
        return ForecastResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
