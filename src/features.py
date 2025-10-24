import pandas as pd
import numpy as np
from sqlalchemy import text
from src.db_setup import get_engine

def _rolling_mean_grouped(df, by, col, window=3):
    """
    Moyenne mobile par groupe, sans fuite temporelle (shift avant rolling).
    """
    df = df.sort_values(by + ["season", "race_id"])
    s = df.groupby(by)[col].apply(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )
    return s.reset_index(level=by, drop=True)

def build_ml_dataset():
    """
    Retourne:
      - df: DataFrame avec features + labels
      - X_cols: liste des colonnes features
    """
    engine = get_engine()
    base_sql = """
    SELECT
      r.race_id, ra.season, ra.round, ra.circuit_id,
      r.driver_id, r.constructor_id,
      r.grid, r.position, r.points
    FROM results r
    JOIN races ra ON ra.race_id = r.race_id
    ORDER BY ra.season, ra.round
    """
    df = pd.read_sql(text(base_sql), engine)

    # Cibles
    df["podium"] = (df["position"].notna()) & (df["position"] <= 3)
    df["podium"] = df["podium"].astype(int)
    df["rank"] = df["position"]  # pour la régression éventuelle

    # Grid: remplace 0/manquant par médiane
    df["grid"] = df["grid"].replace(0, np.nan)
    df["grid"] = df["grid"].fillna(df["grid"].median())

    # --- Features sans fuite ---
    # forme pilote (moyenne rang 3 dernières)
    df["driver_form3"] = _rolling_mean_grouped(df, ["driver_id"], "rank", window=3)
    # forme équipe (points moyens 5 dernières)
    df["team_form5"] = _rolling_mean_grouped(df, ["constructor_id"], "points", window=5)
    # historique pilote-circuit (moyenne rang passé sur ce circuit)
    df["driver_circuit_hist"] = (
        df.sort_values(["driver_id", "circuit_id", "season", "race_id"])
          .groupby(["driver_id", "circuit_id"])["rank"]
          .apply(lambda s: s.shift(1).expanding().mean())
          .reset_index(level=[0,1], drop=True)
    )

    # Remplissages neutres
    for col in ["driver_form3", "team_form5", "driver_circuit_hist"]:
        df[col] = df[col].fillna(df[col].median())

    # grid normalisée par course (rang relatif sur la grille)
    df["grid_norm"] = df.groupby("race_id")["grid"].rank(pct=True)

    X_cols = ["grid", "grid_norm", "driver_form3", "team_form5", "driver_circuit_hist"]
    return df, X_cols

if __name__ == "__main__":
    df, X = build_ml_dataset()
    print(df.head())
    print("Features:", X)

