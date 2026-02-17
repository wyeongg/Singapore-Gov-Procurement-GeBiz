# Singapore Medical Procurement Market Dashboard & AI Assistant

This project explores **Singapore public-sector procurement data** (via GeBIZ) and builds:

1. A **dashboard** to help medical suppliers understand:
   - Market size & trends
   - Top buying agencies
   - Top suppliers & competitors

2. An **AI assistant (chatbot)** that can answer natural-language questions about the same data.
---

## High-level architecture (planned)

Very roughly, the system will look like this:

```text
GeBIZ dataset (data.gov.sg)
          |
          v
    ETL / Ingestion (Python)
          |
          v
  Processed DB (SQLite / Postgres)
          |
          +---------------------+
          |                     |
          v                     v
   REST API (FastAPI)       Offline analysis / notebooks
          |
          v
+---------------------+-------------------------+
|   Dashboard (React) |   AI Chatbot (OpenAI)   |
+---------------------+-------------------------+
```

---

## Running the ETL pipeline

### Prerequisites
- Python 3.9+
- Install dependencies: `pip install -r requirements.txt`

### Run
From the project root:
```bash
python3 -m backend.etl.run_etl
```

This will:
1. Load `data/GovernmentProcurementviaGeBIZ.csv` (18,021 rows)
2. Filter out unusable rows (699 "Awarded to No Suppliers")
3. Clean dates, normalise supplier names, flag suspicious amounts
4. Classify tenders as medical/life-science (hybrid keyword + bigram + agency)
5. Write results to `data/processed/gebiz.db` (SQLite)

Output summary is printed to stdout. The database is overwritten on each run (idempotent).

---

## Running the API server

After running the ETL pipeline at least once:
```bash
python3 -m uvicorn backend.api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Key endpoints:

| Endpoint | Description |
|---|---|
| `GET /health` | Health check + row count |
| `GET /summary/market` | KPI cards (total spend, #tenders, #agencies, #suppliers) |
| `GET /summary/spend-over-time` | Spend aggregated by month or quarter |
| `GET /summary/top-agencies` | Agencies ranked by spend |
| `GET /summary/top-suppliers` | Suppliers ranked by spend |
| `GET /summary/subcategories` | Spend by medical subcategory |
| `GET /tenders` | Search/filter individual tenders |
| `GET /whitespace/agencies` | White-space analysis for a supplier |

Interactive docs at `http://127.0.0.1:8000/docs` (Swagger UI).

---

## Running the dashboard

After running the ETL pipeline and starting the API server:
```bash
cd frontend
npm install        # first time only
npm run dev
```

Open `http://localhost:3000`. The dashboard has two pages:
- **Dashboard** (`/`) — KPI cards, spend chart, top agencies/suppliers table
- **White Space** (`/whitespace`) — find agencies a supplier hasn't reached yet

Add `?embed=true` to hide the nav bar for iframe embedding.

---

### Project structure
```text
backend/
  config.py                    # paths & constants
  api/
    main.py                    # FastAPI REST endpoints
  etl/
    run_etl.py                 # main ETL entry point
    clean.py                   # date parsing, supplier normalisation
    classify.py                # medical/life-science classification
    schema.py                  # SQLite DDL
  services/
    analytics.py               # core analytics + white-space queries
frontend/
  app/                         # Next.js App Router pages
  components/                  # React components (KPI, chart, table, etc.)
  lib/                         # API helpers & formatting utils
data/
  GovernmentProcurementviaGeBIZ.csv   # raw dataset
  processed/
    gebiz.db                   # output SQLite database
docs/
  data-understanding.md        # schema & EDA findings
  product-spec.md              # product specification (v2)
  phase-log.md                 # development roadmap
notebooks/
  lifesci_tender.ipynb         # initial exploration notebook