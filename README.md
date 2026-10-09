# 📈 Influencer Campaign Revenue Prediction

> **Followers don't equal sales.** A regression-based approach to predicting the sales value of influencer marketing campaigns, so budgets go to what actually drives revenue, not just engagement.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-data%20cleaning-150458?logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-regression-F7931E?logo=scikit-learn&logoColor=white)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

---

## 📌 Table of Contents

- [Business Problem](#-business-problem)
- [Project Objectives](#-project-objectives)
- [Dataset](#-dataset)
- [Data Cleaning Workflow](#-data-cleaning-workflow)
- [Cleaning Decisions & Rationale](#-cleaning-decisions--rationale)
- [Results: Before vs. After](#-results-before-vs-after-cleaning)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Roadmap](#-roadmap)
- [Team](#-team)

---

## 🎯 Business Problem

Brands often evaluate influencers using vanity metrics such as follower counts and engagement. These metrics don't necessarily translate into tangible sales, which leads to **wasted marketing budgets and poor investment effectiveness**.

## 🚀 Project Objectives

1. **Build a regression model** that predicts `product_sales` (in dollars) for each influencer marketing campaign.
2. **Enable data-driven budget allocation**, directing spend toward the influencers and platforms that generate the highest financial return, rather than just the highest engagement.

## 📊 Dataset

**File:** `influencer_marketing_roi_dataset.csv`
**Size:** 150,000 campaigns × 10 columns

| Column | Type | Description |
|---|---|---|
| `campaign_id` | string | Unique campaign identifier (e.g. `CAMP100000`) |
| `platform` | categorical | Instagram, YouTube, TikTok, Twitter (X) |
| `influencer_category` | categorical | Food, Tech, Fashion, Gaming, Travel, Beauty, Fitness |
| `campaign_type` | categorical | Seasonal Sale, Product Launch, Brand Awareness, Giveaway, Event Promotion |
| `start_date` | datetime | Campaign start date |
| `end_date` | datetime | Campaign end date |
| `campaign_duration_days` | integer | Duration of the campaign in days |
| `engagements` | integer | Total engagements generated |
| `estimated_reach` | integer | Estimated audience reach |
| **`product_sales`** | integer | **🎯 Target variable**: sales value in dollars |

### Platform Distribution

| Platform | Share | Focus |
|---|---|---|
| Instagram | ~40% | Visual engagement and lifestyle campaigns |
| YouTube | ~30% | In-depth reviews and long-form video |
| TikTok | ~20% | Short-form viral trends |
| Twitter (X) | ~10% | Trend-based and text-heavy promotions |

### Feature Groups

- **Influencer data:** `platform`, `influencer_category`
- **Campaign details:** `campaign_type`, `start_date`, `end_date`, `campaign_duration_days`
- **Performance metrics:** `engagements`, `estimated_reach`
- **Target:** `product_sales`

## 🧹 Data Cleaning Workflow

The original dataset was clean (0 missing values, 0 duplicates). To demonstrate a realistic, reproducible cleaning pipeline, the project follows a **corrupt → detect → fix → verify** approach:

```
1. Load & Inspect      →  keep an untouched copy (df_original), fix random seed (42)
2. Corrupt on Purpose  →  inject realistic data quality problems
3. Quality Analysis    →  detect every problem and capture a "before" snapshot
4. Cleaning Decisions  →  fix each issue with a documented reason
5. Verify              →  capture an "after" snapshot and compare
```

### Injected Problems

| Problem | How it was injected |
|---|---|
| **Outliers** | 20 random rows had `product_sales` set to 10× the max value |
| **Impossible values** | 10 rows had `campaign_duration_days = -5` |
| **Inconsistent text** | 1% of `platform` values lowercased (e.g. `tiktok`) |
| **Missing values** | `estimated_reach` (5%), `engagements` (3%), `platform` (2%) |
| **Duplicates** | 1,000 rows randomly copied and appended |

## 🔧 Cleaning Decisions & Rationale

| Issue | Fix | Why |
|---|---|---|
| Duplicate rows | `drop_duplicates(subset="campaign_id", keep="first")` | Same campaign counted twice inflates its weight in the model. Checking by ID catches duplicates even if one value differs. |
| Inconsistent platform text | `.str.strip().str.title()` + explicit mapping (`TikTok`, `YouTube`) | `tiktok` and `TikTok` are the same platform; otherwise the model treats them as two categories. |
| Negative duration | Recompute as `end_date − start_date` | The dates are intact, so the correct value can be recovered without losing rows. |
| Missing numeric values | Fill with the column mean | The distributions are symmetric (mean ≈ median), and dropping rows would lose ~7% of the data. |
| Missing platform | Fill with `"Unknown"` | Text has no mean, and inventing a platform would add noise. |
| Sales outliers | Keep only `product_sales <= 4999` | The 20 injected values were 10× the true maximum while the rest of the data is evenly distributed, so these are impossible rather than exceptional. |

> ⚠️ **Note on dates:** `pandas` datetime cannot represent dates beyond the year 2262, so date recomputation uses Python's `datetime` module. Dates up to 2432 present in the source were identified as a source-data issue with no reliable correct value, so they were left untouched and are **not used as features**.

## ✅ Results: Before vs. After Cleaning

| Metric | Before | After |
|---|---|---|
| Rows | 151,000 | 149,980 |
| Missing values | 15,098 | **0** |
| Duplicates | 1,000 | **0** |
| Max `product_sales` | 49,990 | **≤ 4,999** |
| Min `campaign_duration_days` | −5 | **> 0** |

**1,020 rows removed** (1,000 duplicates + 20 impossible sales values). Every missing value was resolved, and negative durations were recomputed from dates so no campaign was lost to them.

A final integrity check confirms that exactly the 20 removed outlier IDs are the only campaign IDs missing from the cleaned data, proving nothing was deleted by mistake.

## 📁 Project Structure

```
├── data/
│   ├── influencer_marketing_roi_dataset.csv   # original dataset
│   ├── influencer_dirty.csv                   # intentionally corrupted version
│   └── influencer_clean.csv                   # cleaned output
├── notebooks/
│   └── data_understanding_cleaning.ipynb
├── docs/
│   ├── Data_Understanding_Cleaning.pdf        # cleaning presentation
│   └── Project_Presentation.pdf               # business overview
└── README.md
```

> Adjust the structure above to match your actual repository layout.

## ⚙️ Getting Started

**Prerequisites**

```bash
pip install pandas numpy scikit-learn jupyter
```

**Run**

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
jupyter notebook notebooks/data_understanding_cleaning.ipynb
```

The pipeline uses `np.random.seed(42)`, so the corruption step is fully reproducible.

## 🗺️ Roadmap

- [x] Business problem definition
- [x] Data understanding and quality analysis
- [x] Data cleaning with before/after verification
- [ ] Exploratory data analysis (sales by platform, category, campaign type)
- [ ] Feature engineering and encoding of categorical variables
- [ ] Train and compare regression models (Linear Regression, Random Forest, Gradient Boosting)
- [ ] Evaluate with MAE, RMSE, and R²
- [ ] Feature importance and budget allocation recommendations

## 👥 Team

| Name |
|---|
| **Fatima Anwar Alkhatib** |
| **Zaina Mohamadieh** |
| **Osama Habash** |
| **Rahaf Hani** |

---

⭐ If you found this project useful, consider giving it a star!
