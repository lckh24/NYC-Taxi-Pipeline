from pathlib import Path
from typing import List

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SEED_DIR = DATA_DIR / "seed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
EXPORT_DIR = DATA_DIR / "export"
DB_PATH = WAREHOUSE_DIR / "nyc_taxi.duckdb"

# Data Sources
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

# Network Settings
CHUNK_SIZE = 1024 * 1024  
REQUEST_TIMEOUT = 60

def get_trip_url(year: int, month: int, taxi_type: str = "yellow") -> str:
    """Generate download URL for NYC TLC taxi parquet files."""
    return f"{BASE_URL}/{taxi_type}_tripdata_{year}-{month:02d}.parquet"

def get_trip_urls(year: int, start_month: int, end_month: int, taxi_type: str = "yellow") -> List[str]:
    """Generate a list of download URLs for a range of months."""
    return [get_trip_url(year, m, taxi_type) for m in range(start_month, end_month + 1)]
