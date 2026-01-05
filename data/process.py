"""
Process raw USAJOBS API responses into weekly aggregated time series.
Converts individual postings to weekly counts and optional average salary.
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import argparse


def extract_posting_date(posting: dict) -> Optional[str]:
    """Extract date posted from a job posting."""
    try:
        # USAJOBS date format varies, try multiple paths
        position = posting.get("MatchedObjectDescriptor", {})
        
        # Try PositionFormattedDescription -> PositionRemuneration -> PositionStartDate
        remuneration = position.get("PositionRemuneration", [{}])[0]
        if remuneration:
            start_date = remuneration.get("PositionStartDate")
            if start_date:
                return start_date
        
        # Try PositionSchedule -> StartDate
        schedule = position.get("PositionSchedule", [{}])[0]
        if schedule:
            start_date = schedule.get("StartDate")
            if start_date:
                return start_date
        
        # Try PublicationStartDate
        pub_date = position.get("PublicationStartDate")
        if pub_date:
            return pub_date
        
        # Fallback: PositionPostingDate
        post_date = position.get("PositionPostingDate")
        if post_date:
            return post_date
        
        return None
    except Exception:
        return None


def extract_salary(posting: dict) -> Optional[float]:
    """Extract salary from a job posting."""
    try:
        position = posting.get("MatchedObjectDescriptor", {})
        remuneration = position.get("PositionRemuneration", [{}])
        
        if not remuneration:
            return None
        
        # Try to get minimum or maximum salary
        for rem in remuneration:
            min_salary = rem.get("MinimumRange", {}).get("Value")
            max_salary = rem.get("MaximumRange", {}).get("Value")
            
            if min_salary and max_salary:
                return (float(min_salary) + float(max_salary)) / 2
            elif min_salary:
                return float(min_salary)
            elif max_salary:
                return float(max_salary)
        
        return None
    except Exception:
        return None


def process_raw_to_weekly(input_json: Path, output_csv: Optional[Path] = None) -> pd.DataFrame:
    """
    Process raw JSON data into weekly aggregated time series.
    
    Args:
        input_json: Path to raw JSON file
        output_csv: Optional output CSV path
        
    Returns:
        DataFrame with columns: week_start, postings_count, avg_salary
    """
    print(f"Reading {input_json}...")
    
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get("results", [])
    
    # Extract dates and salaries
    postings_data = []
    for posting in results:
        date_str = extract_posting_date(posting)
        salary = extract_salary(posting)
        
        if date_str:
            try:
                # Parse date (handle various formats)
                date_obj = pd.to_datetime(date_str).date()
                postings_data.append({
                    "date": date_obj,
                    "salary": salary
                })
            except Exception:
                continue
    
    if not postings_data:
        raise ValueError("No valid postings with dates found in input file")
    
    df = pd.DataFrame(postings_data)
    
    # Group by week (week starts on Monday)
    df['week_start'] = pd.to_datetime(df['date']) - pd.to_timedelta(
        pd.to_datetime(df['date']).dt.dayofweek, unit='d'
    )
    
    weekly = df.groupby('week_start').agg({
        'date': 'count',  # Count postings
        'salary': 'mean'  # Average salary
    }).reset_index()
    
    weekly.columns = ['week_start', 'postings_count', 'avg_salary']
    weekly['week_start'] = weekly['week_start'].dt.date
    weekly = weekly.sort_values('week_start').reset_index(drop=True)
    
    # Fill missing weeks with 0 (optional, but useful for time series)
    if len(weekly) > 0:
        min_date = weekly['week_start'].min()
        max_date = weekly['week_start'].max()
        
        # Generate all weeks in range
        all_weeks = pd.date_range(
            start=min_date,
            end=max_date,
            freq='W-MON'
        ).date
        
        weekly_full = pd.DataFrame({'week_start': all_weeks})
        weekly = weekly_full.merge(weekly, on='week_start', how='left')
        weekly['postings_count'] = weekly['postings_count'].fillna(0).astype(int)
        weekly = weekly.sort_values('week_start').reset_index(drop=True)
    
    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        weekly.to_csv(output_csv, index=False)
        print(f"Saved weekly aggregates to {output_csv}")
        print(f"  Total weeks: {len(weekly)}")
        print(f"  Date range: {weekly['week_start'].min()} to {weekly['week_start'].max()}")
        print(f"  Total postings: {weekly['postings_count'].sum()}")
    
    return weekly


def main():
    parser = argparse.ArgumentParser(description="Process raw USAJOBS data to weekly time series")
    parser.add_argument("--input", required=True, help="Input JSON file from fetch_usajobs.py")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--role", default="", help="Role name for output filename")
    parser.add_argument("--location", default="", help="Location for output filename")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    if not args.output:
        # Generate output filename
        if args.role and args.location:
            output_name = f"{args.role.lower().replace(' ', '_')}_{args.location.lower().replace(' ', '_').replace(',', '')}.csv"
        else:
            output_name = input_path.stem + "_weekly.csv"
        args.output = f"data/processed/{output_name}"
    
    output_path = Path(args.output)
    
    try:
        df = process_raw_to_weekly(input_path, output_path)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
