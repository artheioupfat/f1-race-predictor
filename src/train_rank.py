# src/train_rank.py
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

from src.features import build_ml_dataset
from src.splits import time_based_mask  # src/splits.py que tu as déjà créé

def main():
    # Dataset + features
    df, X_cols = build_ml_dataset()

    # garder uniquement les lignes avec un rang défini (exclut DNF sans position)
    df = df.dropna(subset=["rank"]).copy()

    # Split temporel (entraînement < 2024, test = 2024)
    tr_mask, te_mask = time_based_mask(df, test_seasons=(2024,))
    X_tr, y_tr = df.loc[tr_mask, X_cols], df.loc[tr_mask, "rank"]
    X_te, y_te = df.loc[te_mask, X_cols], df.loc[te_mask, "rank"]

    # Modèle
    reg = RandomForestRegressor(
        n_estimators=600,
        random_state=42,
        n_jobs=-1
    )
    reg.fit(X_tr, y_tr)

    # Évaluation
    y_pred = reg.predict(X_te)
    y_pred_clamped = np.clip(np.round(y_pred), 1, 20)

    print("== Test 2024 ==")
    print("MAE (brut):", mean_absolute_error(y_te, y_pred))
    print("MAE (arrondi/clampé 1..20):", mean_absolute_error(y_te, y_pred_clamped))
    print("R² (brut):", r2_score(y_te, y_pred))

    # Sauvegarde
    Path("data/models").mkdir(parents=True, exist_ok=True)
    joblib.dump(reg, "data/models/rank_rf.joblib")
    print("✅ Modèle sauvegardé -> data/models/rank_rf.joblib")

if __name__ == "__main__":
    main()
