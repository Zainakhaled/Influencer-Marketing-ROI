import os, json, hmac, sqlite3, joblib, pandas as pd
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, abort, session

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("DB_PATH", os.path.join(BASE, "roi.db"))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")   # set a real one in production
MODEL = joblib.load(os.path.join(BASE, "model.joblib"))
META = json.load(open(os.path.join(BASE, "meta.json")))
STATS = json.load(open(os.path.join(BASE, "stats.json")))
R = META["ranges"]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

GLOSSARY = [
 ("Your inputs", "Handle", "Your public name on the platform.", "Only used to label your result and to show your campaign to the admin."),
 ("Your inputs", "Platform", "The social network where the campaign runs: Instagram, YouTube, TikTok or Twitter.", "In the data, YouTube and Instagram campaigns sell the most."),
 ("Your inputs", "Influencer category", "Your niche: Beauty, Fashion, Fitness, Food, Gaming, Tech or Travel.", "Tech creators sell noticeably more than the other niches in this data."),
 ("Your inputs", "Campaign type", "What the campaign is trying to achieve.", "Brand Awareness: get seen, not necessarily sell. Event Promotion: fill an event. Giveaway: free product in exchange for follows or shares. Product Launch: introduce a new product (the strongest seller in the data). Seasonal Sale: a limited-time offer tied to a season or holiday."),
 ("Your inputs", "Engagements", "Total likes, comments, shares and saves your campaign posts received.", "Find it in the analytics or insights section of your platform. It is the single biggest driver of sales in the model."),
 ("Your inputs", "Estimated reach", "How many different people saw or could have seen the campaign content.", "Also in your platform's analytics. Reach counts people, not views, so one person seeing a post twice counts once."),
 ("Your inputs", "Campaign duration", "Days from the first post to the last post of the campaign.", "Longer campaigns sell more, but the model only knows campaigns from 1 to 29 days."),
 ("Results", "Expected sales", "How many units of the product the model expects your campaign to sell.", "A planning estimate, not a promise."),
 ("Results", "Typical range", "Expected sales minus and plus the model's average error (about 400 units).", "Real results usually land inside this band."),
 ("Results", "Engagement rate", "Engagements divided by reach, shown as a percentage.", "Looks high when reach is small. Compare it with your own past campaigns."),
 ("Results", "Average campaign", "The average sales of all campaigns in the dataset (about 5,340 units).", "Your result is compared against it so you can see if you are above or below normal."),
 ("Model and data", "Lasso regression", "The model that makes the estimate. It is a straight-line model that pushes unimportant factors toward zero.", "It beat Random Forest and Gradient Boosting in testing."),
 ("Model and data", "R²", "The share of the differences in sales that the model explains. 94.7% here.", "100% would be perfect prediction."),
 ("Model and data", "RMSE", "The typical size of the model's mistakes, in units of sales (about 400).", "Guessing the average every time would give a typical mistake of about 1,700."),
 ("Model and data", "Permutation importance", "A way to rank factors: scramble one factor and see how much the model gets worse.", "Used in the notebook to find that engagements and duration matter most."),
 ("Model and data", "Training range", "The span of values the model has seen: engagements 100 to 99,999, reach 1,000 to 1,000,000, duration 1 to 29 days.", "Outside this range the estimate would be a guess, so the form does not accept it."),
 ("Model and data", "Model-ready sales", "In the original file the sales column was random and unrelated to anything else, so the project rebuilt it from business rules (Milestone 3).", "All dashboards and the model use this rebuilt column."),
]

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT DEFAULT CURRENT_TIMESTAMP,
        handle TEXT, platform TEXT, category TEXT, campaign_type TEXT,
        engagements INTEGER, reach INTEGER, days INTEGER, eng_rate REAL, predicted INTEGER)""")
    return con

def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("admin"): return redirect(url_for("admin"))
        return f(*a, **k)
    return w

def predict(platform, category, ctype, eng, reach, days):
    row = dict.fromkeys(META["columns"], 0)
    row.update(engagements=eng, estimated_reach=reach, campaign_duration_days=days, engagement_rate=eng / reach)
    for col in (f"platform_{platform}", f"influencer_category_{category}", f"campaign_type_{ctype}"):
        if col in row: row[col] = 1
    return max(50, round(float(MODEL.predict(pd.DataFrame([row])[META["columns"]])[0])))

@app.get("/")
def home():
    return render_template("landing.html", n=STATS["All"]["n"])

@app.get("/guide")
def guide():
    groups = {}
    for g, term, short, more in GLOSSARY: groups.setdefault(g, []).append((term, short, more))
    return render_template("guide.html", groups=groups)

@app.get("/influencer")
def influencer():
    return render_template("influencer.html", m=META, err=request.args.get("err"))

@app.post("/submit")
def submit():
    f, o = request.form, META["options"]
    try:
        handle = f["handle"].strip().lstrip("@")[:60]
        platform, cat, ctype = f["platform"], f["category"], f["campaign_type"]
        eng, reach, days = int(f["engagements"]), int(f["reach"]), int(f["days"])
    except (KeyError, ValueError):
        return redirect(url_for("influencer", err="Please fill in every field with valid numbers."))
    if not handle or platform not in o["platform"] or cat not in o["influencer_category"] or ctype not in o["campaign_type"]:
        return redirect(url_for("influencer", err="Please fill in every field."))
    for name, v, (lo, hi) in (("Engagements", eng, R["engagements"]), ("Reach", reach, R["estimated_reach"]), ("Duration", days, R["duration"])):
        if not lo <= v <= hi:
            return redirect(url_for("influencer", err=f"{name} must be between {lo:,} and {hi:,}, the range the model was trained on."))
    p = predict(platform, cat, ctype, eng, reach, days)
    with db() as con:
        cur = con.execute("INSERT INTO submissions(handle,platform,category,campaign_type,engagements,reach,days,eng_rate,predicted) VALUES(?,?,?,?,?,?,?,?,?)",
                          (handle, platform, cat, ctype, eng, reach, days, eng / reach, p))
    return redirect(url_for("result", sid=cur.lastrowid))

@app.get("/result/<int:sid>")
def result(sid):
    r = db().execute("SELECT * FROM submissions WHERE id=?", (sid,)).fetchone() or abort(404)
    return render_template("result.html", r=r, m=META, diff=(r["predicted"] - META["avg_sales"]) / META["avg_sales"] * 100)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    err = None
    if request.method == "POST":
        if hmac.compare_digest(request.form.get("password", "").encode(), ADMIN_PASSWORD.encode()): session["admin"] = True
        else: err = "Wrong password."
    if not session.get("admin"): return render_template("admin_login.html", err=err)
    n = db().execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    return render_template("admin_hub.html", n=n, rows=STATS["All"]["n"])

@app.get("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.get("/admin/submissions")
@admin_required
def admin_submissions():
    con = db()
    t = con.execute("SELECT COUNT(*) n, AVG(predicted) p, AVG(eng_rate) e FROM submissions").fetchone()
    grp = lambda col: [dict(x) for x in con.execute(f"SELECT {col} k, COUNT(*) n, AVG(predicted) p FROM submissions GROUP BY {col} ORDER BY p DESC")]
    recent = con.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 15").fetchall()
    return render_template("admin_submissions.html", t=t, m=META, recent=recent, by_platform=grp("platform"), by_type=grp("campaign_type"), by_cat=grp("category"))

@app.get("/admin/dataset")
@admin_required
def admin_dataset():
    return render_template("admin_dataset.html", stats=STATS)

@app.get("/dashboard")
def old_dashboard(): return redirect(url_for("admin_submissions"))

@app.template_filter("n")
def fmt(v): return f"{v:,.0f}"

if __name__ == "__main__":
    app.run(debug=True)
