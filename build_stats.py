"""Pre-computes the aggregates for the admin dataset dashboard -> stats.json"""
import json, numpy as np, pandas as pd
from pipeline import load_clean
df = load_clean(); R = lambda s: [round(float(x)) for x in s]

def block(d):
    g = lambda c: d.groupby(c)["product_sales"].mean().sort_values(ascending=False)
    cat, typ = g("influencer_category"), g("campaign_type")
    dur = d.groupby(pd.cut(d.campaign_duration_days, [0, 6, 12, 18, 24, 29], labels=["1-6", "7-12", "13-18", "19-24", "25-29"]), observed=True)["product_sales"].mean()
    band = d.groupby(pd.qcut(d.engagements, 10, labels=False, duplicates="drop"))["product_sales"].mean()
    cnt, edges = np.histogram(d.product_sales, bins=10)
    return dict(n=len(d), sales=round(d.product_sales.mean()), eng=round(d.engagements.mean()), reach=round(d.estimated_reach.mean()),
        days=round(d.campaign_duration_days.mean(), 1),
        category=dict(labels=list(cat.index), values=R(cat)), type=dict(labels=list(typ.index), values=R(typ)),
        duration=dict(labels=[str(i) for i in dur.index], values=R(dur)),
        band=dict(labels=[f"{int(i)+1}" for i in band.index], values=R(band)),
        hist=dict(labels=[f"{a/1000:.1f}k" for a in edges[:-1]], counts=cnt.tolist()))

pl = df.groupby("platform")["product_sales"].agg(["mean", "size"]).sort_values("mean", ascending=False)
out = {"All": block(df), "platforms": dict(labels=list(pl.index), sales=R(pl["mean"]), count=[int(x) for x in pl["size"]])}
for p in ["Instagram", "YouTube", "TikTok", "Twitter"]:
    out[p] = block(df[df.platform == p])
json.dump(out, open("stats.json", "w"))
print(out["All"]["n"], out["All"]["band"], out["All"]["duration"])
raw = pd.read_csv("data/influencer_marketing_roi_dataset.csv")
print("raw corr sales~engagements:", round(raw.product_sales.corr(raw.engagements), 3))
