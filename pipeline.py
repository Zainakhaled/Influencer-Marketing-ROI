"""Shared cleaning + sales rules from the notebook (Milestones 2-3)."""
import numpy as np, pandas as pd

def load_clean(path="data/influencer_marketing_roi_dataset.csv"):
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="campaign_id")
    df["platform"] = df["platform"].str.strip().str.title().replace({"Tiktok": "TikTok", "Youtube": "YouTube"}).fillna("Unknown")
    df = df[(df["product_sales"] <= 4999) & (df["campaign_duration_days"] > 0)].copy()
    for c in ["estimated_reach", "engagements"]:
        df[c] = df[c].fillna(df[c].mean())
    np.random.seed(42)
    s = (0.03*df["engagements"] + 0.002*df["estimated_reach"] + 100*df["campaign_duration_days"]
         + (df["platform"] == "YouTube")*1500 + (df["platform"] == "Instagram")*1000
         + (df["campaign_type"] == "Product Launch")*1800 + (df["influencer_category"] == "Tech")*900
         + np.random.normal(0, 400, len(df)))
    df["product_sales"] = np.maximum(s, 50).round().astype(int)
    df["engagement_rate"] = df["engagements"] / df["estimated_reach"]
    df["start_date"] = pd.to_datetime(df["start_date"])
    return df
