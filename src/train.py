from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
from sklearn.ensemble import RandomForestClassifier
from src.features import build_ml_dataset

def train_podium_model():
    df, X_cols = build_ml_dataset()
    df = df.dropna(subset=["position"])
    X = df[X_cols]
    y = df["podium"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    clf = RandomForestClassifier(n_estimators=300, random_state=42)
    clf.fit(X_tr, y_tr)
    preds = clf.predict(X_te)
    print(classification_report(y_te, preds))
    return clf

if __name__ == "__main__":
    train_podium_model()
    