"""
Configuration settings for the backend application.
"""
import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    ARTIFACTS_DIR = BASE_DIR / "backend" / "app" / "artifacts"
    DATA_DIR = BASE_DIR / "data" / "processed"
    
    # API settings
    API_TITLE = "Job Market Demand Forecaster API"
    API_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Model settings
    DEFAULT_WINDOW_SIZE = 12
    DEFAULT_HORIZON = 8
    MAX_HISTORY_WEEKS = 104
    
    @classmethod
    def get_artifacts_path(cls, role: str, location: str) -> Path:
        """Get path to model artifacts for a role/location."""
        role_slug = role.lower().replace(" ", "_")
        # Handle location: replace comma+space with underscore, then replace any remaining spaces
        location_slug = location.lower().replace(", ", "_").replace(",", "_").replace(" ", "_")
        # Remove double underscores
        while "__" in location_slug:
            location_slug = location_slug.replace("__", "_")
        return cls.ARTIFACTS_DIR / f"{role_slug}_{location_slug}"


settings = Settings()
