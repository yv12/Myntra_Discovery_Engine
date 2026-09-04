# 🛍️ Myntra Discovery Engine: Wishlist-to-Purchase Conversion

> **An empirical, multi-corpus product discovery pipeline analyzing pre-purchase hesitation, verification barriers, and conversion levers for Myntra shoppers.**

---

## 📌 Executive Summary (Product & Project Management View)

### The Problem
While millions of items are added to Myntra wishlists daily, a significant proportion never convert into purchases within 30 days. For Product and Growth teams, the core question is:
> **When a shopper saves an item to their wishlist, what prevents them from buying it, and what product interventions will unlock conversion?**

### What We Built
The **Myntra Discovery Engine** is an automated qualitative research and analytics engine that ingests, filters, classifies, and ranks pre-purchase friction points across **4 independent data sources** using a combination of LLM-based taxonomy classification, deterministic source-weighted scoring, and Retrieval-Augmented Generation (RAG).

```
   63,014 Play Store Reviews ──┐
   45 Reddit Community Records ─┼──► [4-Gate Filter Pipeline] ──► [LLM Classification] ──► [Weighted Scoring] ──► [RAG + Dashboard]
   39 Consumer Survey Responses ┼     (Isolates 384 high-intent     (5-D Closed Taxonomy)    (Pure Python Math)      (PM Insights)
   4 In-Depth User Interviews ──┘      pre-purchase records)
```

---

## 🔍 Key Findings & Product Discovery Insights

### 1. Eliminating Complaint Bias via Source Reweighting
* **The Trap**: Raw app store reviews are 99.5% post-purchase operational noise. Unfiltered data falsely suggests **delivery serviceability** (42.6%) is the #1 problem.
* **The Reality**: Deep primary research reveals that **psychological deliberation** (quality doubts, lack of reviews, return anxiety) drives actual hesitation.
* **The Fix**: Applying calibrated source weights (`Interviews: 4.0×` > `Surveys: 3.0×` > `Reddit: 1.5×` > `Play Store: 1.0×`) elevates **Quality Doubt** (`quality_doubt`) to the **#1 overall product blocker**.

| Rank | Blocker Type | Category | Weighted Score | Stated Elasticity | Primary Driver |
|:---:|---|---|:---:|:---:|---|
| **#1** | **Quality Doubt** | Product Trust | **1.6593** | 25.0% | Fear of thin fabric, fake discounts, studio photo deception |
| **#2** | **Price Wait** | Economic | **0.6515** | 62.5% | Waiting for EORS sales / coupon discounts |
| **#3** | **No Reviews / Photos**| Social Proof | **0.5599** | 50.0% | Zero customer photos or unedited reviews on newer listings |
| **#4** | **Budget Constraint** | Economic | **0.3950** | 50.0% | Saving items until month-end salary payout |
| **#5** | **Decision Paralysis** | UX / Cognitive | **0.3608** | 42.9% | Comparison overload across 3–5 similar items |

---

### 2. Shopper Personas & Behavioral Archetypes (n=4 Interviews)

* 💼 **The Disciplined Luxury Planner (P1)**: Uses the wishlist as a curated budget queue for high-ticket items (₹15k–₹40k). Waits for liquidity/bonuses, then purchases directly.
* 📦 **The Return-Anxious Apparel Shopper (P2)**: Abandonment driven by fear of courier return friction. Items lacking reviews or customer photos are abandoned 100% of the time.
* 🧵 **The Tactile / Offline Skeptic (P3)**: Suspects heavily discounted clothes online are factory seconds or defective. Requires offline validation for stitch quality and fit.
* ✨ **The High-Volume Mood Saver (P4)**: Saves dozens of items on impulse and forgets them. Needs real buyer photos to assess fabric drape and Indian skin tone matching.

---

### 3. Strategic Roadmap & Product Interventions

1. **Trust & Verification Layer (Top Product Priority)**:
   * **Verified Customer Photos**: Mandatory prompts for visual fit reviews.
   * **Fabric & GSM Transparency**: Standardized fabric weight, opacity ratings, and stretch indicators to eliminate the "thin cloth" fear.
2. **Dynamic Price & Liquidity Tools**:
   * **90-Day Price Transparency**: Visible price history graphs to eliminate artificial markup skepticism.
   * **Payday / Salary Reminders**: Non-intrusive alerts synced to month-end purchase cycles.
3. **Cart & Inventory Friction Reducers**:
   * **2-Hour Size Lock**: Short-term cart reservations for items with low stock.

---

## 🏗️ Technical Architecture & Pipeline

```
├── config/
│   ├── taxonomy.yaml           # 5-dimension closed classification taxonomy
│   ├── filters.yaml            # 4-gate keyword & length filtering rules
│   ├── scoring.yaml            # Source weights & ownership definitions
│   └── ownership.yaml          # Product / Engineering / Ops squad mapping
├── src/
│   ├── ingest/                 # Raw parsers (Play Store JSONL, Reddit DOCX, Survey XLSX, Interviews)
│   ├── filter.py               # 4-gate sequential rule engine
│   ├── classify.py             # LLM classifier (Groq / GPT-OSS 120B with JSON schema validation)
│   ├── count.py                # Deterministic arithmetic aggregations
│   ├── score.py                # Source-weighted scoring & ranking formulas
│   ├── rag_engine.py           # BM25-grounded RAG engine answering 10 core PM questions
│   └── export_dashboard_data.py# Exports JSON bundles for web visualization
├── dashboard/                  # Interactive HTML/JS Product Analytics Dashboard
└── Docs/
    ├── FINDINGS.md             # Complete research findings & multi-corpus synthesis
    └── engine-architecture.md  # System architecture & verification specs
```

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10+
* Groq API Key (for LLM taxonomy classification)

### 2. Installation
```bash
# Clone repository
git clone https://github.com/yv12/Myntra_Discovery_Engine.git
cd Myntra_Discovery_Engine

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and insert your GROQ_API_KEY
```

### 3. Running the Discovery Pipeline
```bash
# Run the complete pipeline end-to-end
python src/run_ingest.py    # Phase 1: Ingestion
python src/run_filter.py    # Phase 2: 4-Gate Filter
python src/run_classify.py  # Phase 3: Taxonomy Classification
python src/run_count.py     # Phase 4: Deterministic Counts
python src/run_score.py     # Phase 5: Weighted Scoring & Ranking
```

### 4. Viewing the Dashboard
Open [`dashboard/index.html`](dashboard/index.html) in any modern web browser or start a local HTTP server:
```bash
python -m http.server 8000 --directory dashboard
```
Navigate to `http://localhost:8000` to interactively inspect conversion blockers, funnel drop-offs, persona journeys, and RAG Q&A syntheses.

---

## 👥 Contributors & Ownership
* **Analysis & Implementation**: Product Analyst & Discovery Engine Team
* **Target Metric**: 30-Day Wishlist-to-Purchase Conversion Rate