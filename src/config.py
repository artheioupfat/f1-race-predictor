from pathlib import Path

# Emplacements
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw_json"
DB_PATH = DATA_DIR / "f1_races.db"

# Paramètres d’extraction initiale
DEFAULT_SEASONS = list(range(2018, 2025))  # ajustable
# Jolpica : endpoints compatibles Ergast
ERGAST_BASE = "http://api.jolpi.ca/ergast/f1"

