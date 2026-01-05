"""
Fetch job postings from USAJOBS API and cache raw responses.
Handles pagination, rate limiting, and graceful error handling.
"""
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import argparse


class USAJobsFetcher:
    """Fetch job postings from USAJOBS API with rate limiting."""
    
    BASE_URL = "https://data.usajobs.gov/api/Search"
    DEFAULT_DELAY = 0.1  # 100ms between requests (10 req/sec max)
    
    def __init__(self, api_key: Optional[str] = None, user_agent: Optional[str] = None):
        """
        Initialize fetcher with API credentials.
        
        Args:
            api_key: USAJOBS API key (or from USAJOBS_API_KEY env var)
            user_agent: User agent email (or from USAJOBS_USER_AGENT env var)
        """
        self.api_key = api_key or os.getenv("USAJOBS_API_KEY")
        self.user_agent = user_agent or os.getenv("USAJOBS_USER_AGENT")
        
        if not self.api_key or not self.user_agent:
            raise ValueError(
                "USAJOBS API credentials required. "
                "Set USAJOBS_API_KEY and USAJOBS_USER_AGENT environment variables."
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            "Host": "data.usajobs.gov",
            "User-Agent": self.user_agent,
            "Authorization-Key": self.api_key
        })
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Ensure we respect rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.DEFAULT_DELAY:
            time.sleep(self.DEFAULT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def fetch_page(self, keyword: str, location: Optional[str] = None, 
                   date_from: Optional[str] = None, date_to: Optional[str] = None,
                   page: int = 1, page_size: int = 500) -> Dict:
        """
        Fetch a single page of results.
        
        Args:
            keyword: Job role keyword
            location: Optional location filter
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            page: Page number (1-indexed)
            page_size: Results per page (max 500)
            
        Returns:
            JSON response dictionary
        """
        self._rate_limit()
        
        params = {
            "Keyword": keyword,
            "ResultsPerPage": min(page_size, 500),
            "Page": page
        }
        
        if location:
            params["LocationName"] = location
        
        if date_from:
            params["DatePostedFrom"] = date_from
        
        if date_to:
            params["DatePostedTo"] = date_to
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            raise
    
    def fetch_all(self, keyword: str, location: Optional[str] = None,
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  max_pages: Optional[int] = None) -> List[Dict]:
        """
        Fetch all pages of results with pagination.
        
        Returns:
            List of all job postings
        """
        all_results = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
            
            print(f"Fetching page {page}...")
            data = self.fetch_page(keyword, location, date_from, date_to, page)
            
            search_result = data.get("SearchResult", {})
            search_result_items = search_result.get("SearchResultItems", [])
            
            if not search_result_items:
                break
            
            all_results.extend(search_result_items)
            
            # Check if more pages exist
            total_pages = search_result.get("UserArea", {}).get("NumberOfPages", 1)
            if page >= total_pages:
                break
            
            page += 1
        
        print(f"Fetched {len(all_results)} total postings across {page} pages")
        return all_results
    
    def save_raw(self, results: List[Dict], output_path: Path):
        """Save raw results to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "fetched_at": datetime.now().isoformat(),
                "total_results": len(results),
                "results": results
            }, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(results)} results to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch job postings from USAJOBS API")
    parser.add_argument("--keyword", required=True, help="Job role keyword (e.g., 'Software Engineer')")
    parser.add_argument("--location", default=None, help="Location filter (e.g., 'New York, NY')")
    parser.add_argument("--date-from", default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--date-to", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum pages to fetch")
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        role_slug = args.keyword.lower().replace(" ", "_")
        location_slug = (args.location or "all").lower().replace(" ", "_").replace(",", "")
        date_str = datetime.now().strftime("%Y%m%d")
        args.output = f"data/raw/{role_slug}_{location_slug}_{date_str}.json"
    
    output_path = Path(args.output)
    
    try:
        fetcher = USAJobsFetcher()
        results = fetcher.fetch_all(
            keyword=args.keyword,
            location=args.location,
            date_from=args.date_from,
            date_to=args.date_to,
            max_pages=args.max_pages
        )
        fetcher.save_raw(results, output_path)
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nNote: For offline usage, use the sample cached data in data/raw/")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
