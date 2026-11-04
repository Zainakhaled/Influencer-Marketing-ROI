"""Rebuilds the notebook pipeline (Milestones 2-4) and saves the final Lasso model."""
import json, joblib, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

from pipeline import load_clean
df = load_clean()
cats = ["platform", "influencer_category", "campaign_type"]
options = {c: sorted(df[c].unique()) for c in cats}
df = df.drop(columns=["campaign_id", "start_date", "end_date"])
enc = pd.get_dummies(df, columns=cats, drop_first=True, dtype=int).sample(n=10000, random_state=42)

# Milestone 4 - final model (Lasso)
X, y = enc.drop(columns="product_sales"), enc["product_sales"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
pipe = Pipeline([("scaler", StandardScaler()), ("model", Lasso(alpha=1.0, random_state=42))]).fit(Xtr, ytr)
pred = pipe.predict(Xte)
rmse, r2 = float(np.sqrt(mean_squared_error(yte, pred))), float(r2_score(yte, pred))
print(f"Test R2={r2:.4f}  RMSE={rmse:.1f}")

joblib.dump(pipe, "model.joblib")
json.dump({"columns": list(X.columns), "rmse": round(rmse, 1), "r2": round(r2, 4),
           "avg_sales": round(float(df["product_sales"].mean())),
           "ranges": {"engagements": [100, 99999], "estimated_reach": [1000, 1000000], "duration": [1, 29]},
           "options": {k: [v for v in vals if v != "Unknown"] for k, vals in options.items()},
           "coefficients": dict(zip(X.columns, pipe.named_steps["model"].coef_.round(3)))},
          open("meta.json", "w"), indent=1)
