from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import joblib

from src.features import build_ml_dataset
from src.splits import time_based_mask
from pathlib import Path
Path("data/models").mkdir(parents=True, exist_ok=True)


def main():
    df, X_cols = build_ml_dataset()
    y = df["podium"].astype(int)
    X = df[X_cols]

    tr_mask, te_mask = time_based_mask(df, test_seasons=(2024,))
    X_tr, y_tr = X[tr_mask], y[tr_mask]
    X_te, y_te = X[te_mask], y[te_mask]

    # pondération pour la classe 1 (podium) souvent minoritaire
    classes = np.array([0, 1])
    cw = compute_class_weight("balanced", classes=classes, y=y_tr)
    weights = {cls: w for cls, w in zip(classes, cw)}

    clf = RandomForestClassifier(
        n_estimators=600, max_depth=None, random_state=42, n_jobs=-1,
        class_weight=weights
    )
    clf.fit(X_tr, y_tr)

    proba = clf.predict_proba(X_te)[:, 1]
    pred = (proba >= 0.5).astype(int)

    print("== Test saisons:", sorted(df.loc[te_mask, "season"].unique()))
    print(classification_report(y_te, pred, digits=3))
    print("ROC-AUC:", roc_auc_score(y_te, proba))
    print("PR-AUC:", average_precision_score(y_te, proba))

    joblib.dump(clf, "data/models/podium_rf.joblib")
    print("✅ Modèle sauvegardé -> data/models/podium_rf.joblib")

if __name__ == "__main__":
    main()
