import requests
from requests.adapters import HTTPAdapter, Retry
from src.config import ERGAST_BASE

def _session():
    s = requests.Session()
    retries = Retry(
        total=5, backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"])
    )
    s.headers.update({"User-Agent": "f1-race-predictor/0.1 (+github.com/arthurprigent)"})
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

def get_json(url: str) -> dict:
    r = _session().get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_drivers(season: int) -> dict:
    return get_json(f"{ERGAST_BASE}/{season}/drivers.json?limit=1000")

def fetch_constructors(season: int) -> dict:
    return get_json(f"{ERGAST_BASE}/{season}/constructors.json?limit=1000")

def fetch_circuits(season: int) -> dict:
    return get_json(f"{ERGAST_BASE}/{season}/circuits.json?limit=1000")

def fetch_results(season: int) -> dict:
    return get_json(f"{ERGAST_BASE}/{season}/results.json?limit=1000")
