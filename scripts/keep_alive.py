#!/usr/bin/env python3
"""
Keep-alive script to prevent Render service from going idle.
Run this script periodically (e.g., every 10 minutes) from:
- Your local machine (while it's on)
- GitHub Actions (free, runs on schedule)
- Another free service (PythonAnywhere, etc.)

Usage:
    python scripts/keep_alive.py https://your-app.onrender.com

Or set RENDER_URL environment variable:
    export RENDER_URL=https://your-app.onrender.com
    python scripts/keep_alive.py

Dependencies:
    pip install requests
    OR use urllib (built-in, no install needed - update USE_URLLIB=True below)
"""
import os
import sys
from datetime import datetime

# Try to use requests, fallback to urllib if not available
USE_URLLIB = False  # Set to True to use built-in urllib instead of requests

if not USE_URLLIB:
    try:
        import requests
    except ImportError:
        USE_URLLIB = True
        import urllib.request
        import json

if USE_URLLIB:
    import urllib.request
    import urllib.error
    import json


def ping_service(url):
    """Ping the service health endpoint."""
    # Try /health first, then /ping
    endpoints = ['/health', '/ping']
    
    for endpoint in endpoints:
        full_url = f"{url.rstrip('/')}{endpoint}"
        try:
            if USE_URLLIB:
                # Use built-in urllib
                req = urllib.request.Request(full_url)
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping successful: {endpoint}")
                        print(f"   Response: {data}")
                        return True
            else:
                # Use requests
                response = requests.get(full_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping successful: {endpoint}")
                    print(f"   Response: {data}")
                    return True
        except Exception as e:
            # Try next endpoint
            continue
    
    print(f"❌ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping failed on all endpoints")
    return False


def main():
    # Get URL from command line or environment variable
    url = sys.argv[1] if len(sys.argv) > 1 else os.getenv('RENDER_URL')
    
    if not url:
        print("❌ Error: No URL provided")
        print("\nUsage:")
        print("  python scripts/keep_alive.py https://your-app.onrender.com")
        print("  OR")
        print("  export RENDER_URL=https://your-app.onrender.com")
        print("  python scripts/keep_alive.py")
        sys.exit(1)
    
    print(f"🔔 Pinging service: {url}")
    success = ping_service(url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
