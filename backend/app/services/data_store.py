"""
Data store service for reading time series data.
"""
import pandas as pd
from pathlib import Path
from typing import List, Optional
from datetime import date, timedelta
from backend.app.config import settings


class DataStore:
    """Service for accessing time series data."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize data store.
        
        Args:
            data_dir: Directory containing processed CSV files
        """
        self.data_dir = Path(data_dir) if data_dir else settings.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_csv_path(self, role: str, location: str) -> Path:
        """Get path to CSV file for role/location."""
        role_slug = role.lower().replace(" ", "_")
        # Handle location: replace comma+space with underscore, then replace any remaining spaces
        location_slug = location.lower().replace(", ", "_").replace(",", "_").replace(" ", "_")
        # Remove double underscores
        while "__" in location_slug:
            location_slug = location_slug.replace("__", "_")
        filename = f"{role_slug}_{location_slug}.csv"
        csv_path = self.data_dir / filename
        print(f"[DEBUG] Looking for data CSV at: {csv_path}")
        return csv_path
    
    def load_series(
        self,
        role: str,
        location: str,
        max_weeks: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load time series data for a role/location.
        
        Args:
            role: Job role name
            location: Location name
            max_weeks: Maximum number of weeks to return (default: all)
            
        Returns:
            DataFrame with columns: week_start, postings_count
            
        Raises:
            FileNotFoundError: If data file not found
        """
        csv_path = self.get_csv_path(role, location)
        
        if not csv_path.exists():
            raise FileNotFoundError(
                f"No data found for role '{role}' and location '{location}'. "
                f"Expected file: {csv_path}"
            )
        
        df = pd.read_csv(csv_path)
        df['week_start'] = pd.to_datetime(df['week_start']).dt.date
        
        # Sort by date (ascending)
        df = df.sort_values('week_start').reset_index(drop=True)
        
        # Limit to max_weeks (most recent)
        if max_weeks:
            df = df.tail(max_weeks).reset_index(drop=True)
        
        return df[['week_start', 'postings_count']]
    
    def get_latest_date(self, role: str, location: str) -> Optional[date]:
        """Get the latest date in the time series."""
        try:
            df = self.load_series(role, location, max_weeks=1)
            if len(df) > 0:
                return df['week_start'].iloc[-1]
        except FileNotFoundError:
            pass
        return None
    
    def to_time_series_points(self, df: pd.DataFrame) -> List[dict]:
        """Convert DataFrame to list of TimeSeriesPoint-like dicts."""
        return [
            {
                "week_start": str(row['week_start']),
                "value": float(row['postings_count'])
            }
            for _, row in df.iterrows()
        ]


# Global instance
data_store = DataStore()
