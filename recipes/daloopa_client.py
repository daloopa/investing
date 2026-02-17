"""
Daloopa API client — shared auth and request helpers used by all recipes.

Setup:
    export DALOOPA_EMAIL="you@example.com"
    export DALOOPA_API_KEY="your_api_key"

Or create a .env file in the project root with those values.
"""

import base64
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

BASE_URL = "https://app.daloopa.com/api/v2"
RATE_LIMIT = 120  # requests per minute


def _load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def get_headers() -> dict:
    """Build Basic Auth headers from environment variables."""
    email = os.environ.get("DALOOPA_EMAIL", "")
    api_key = os.environ.get("DALOOPA_API_KEY", "")
    if not email or not api_key:
        raise EnvironmentError(
            "Set DALOOPA_EMAIL and DALOOPA_API_KEY environment variables "
            "(or add them to .env in the project root)."
        )
    credentials = base64.b64encode(f"{email}:{api_key}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}


def get(path: str, params: dict | None = None) -> dict | list:
    """GET request with auth. Returns parsed JSON."""
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, headers=get_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def post(path: str, json_body: dict | None = None) -> dict | list:
    """POST request with auth. Returns parsed JSON."""
    url = f"{BASE_URL}{path}"
    resp = requests.post(url, headers=get_headers(), json=json_body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def download(path: str, dest: str, params: dict | None = None) -> str:
    """Download a file (CSV, Excel) to dest path. Returns the path written."""
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, headers=get_headers(), params=params, timeout=60, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return dest


def paginate(path: str, params: dict | None = None) -> list:
    """Auto-paginate a list endpoint that returns {count, next, results}."""
    params = dict(params or {})
    all_results = []
    while True:
        data = get(path, params)
        if isinstance(data, list):
            return data
        all_results.extend(data.get("results", []))
        if not data.get("next"):
            break
        params["offset"] = params.get("offset", 0) + len(data.get("results", []))
    return all_results
