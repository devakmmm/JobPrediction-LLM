"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class TimeSeriesPoint(BaseModel):
    """A single time series data point."""
    week_start: str = Field(..., description="Week start date (ISO format)")
    value: float = Field(..., description="Postings count")


class ForecastResponse(BaseModel):
    """Forecast API response."""
    role: str = Field(..., description="Job role")
    location: str = Field(..., description="Location")
    history: List[TimeSeriesPoint] = Field(..., description="Historical data points")
    forecast: List[TimeSeriesPoint] = Field(..., description="Forecasted values")
    model: dict = Field(..., description="Model metadata")


class SeriesResponse(BaseModel):
    """Time series data response."""
    role: str = Field(..., description="Job role")
    location: str = Field(..., description="Location")
    series: List[TimeSeriesPoint] = Field(..., description="Time series data points")


class HealthResponse(BaseModel):
    """Health check response."""
    ok: bool = Field(..., description="Service health status")
