<!-- docs/product-spec-v2.md -->

# Product Spec – Singapore Medical Procurement Market Dashboard & AI Assistant (v2 – with White-Space Analysis)

## 1. Overview

We are building a **web-based dashboard and AI assistant** for medical suppliers interested in Singapore public-sector procurement opportunities.

The product ingests the **Government Procurement via GeBIZ** dataset (Apr 2020 onwards) and focuses on **medical-related tenders**. It presents structured analytics, **white-space views** (where agencies spend in a supplier’s category but have not yet awarded to that supplier), and lets users ask free-text questions via an OpenAI-powered chatbot.

This spec reflects **v2 of the product definition**, incorporating:
- Core market/competition analytics from v1.
- A new **white-space analysis** feature to help suppliers identify expansion opportunities using only award data.

---

## 2. Target users & persona

### Primary persona

- Role: Business development / sales manager, founder, or strategic planner at a **medical supplier** (devices, consumables, diagnostics, services).
- Goals:
  - Understand **who buys what**, **who wins**, and **how big the opportunity is** in Singapore’s public sector.
  - Identify **where they are NOT yet winning** despite meaningful spend in their product area (white space).

### Secondary persona

- Consultants / analysts supporting medical suppliers.
- Researchers exploring public-sector healthcare spending patterns.

---

## 3. Data source & assumptions

- **Source:** Government Procurement via GeBIZ dataset from data.gov.sg.
- **Time range:** Apr 2020 – latest available award date.
- **Granularity:** Tender-level award records.
- **Medical focus:** Determined through a **classification strategy** on `tender_description` and `agency`.

Assumptions:

- Award records correctly represent actual spend (subject to data quality checks).
- Medical tenders can be reasonably approximated using rule-based classification on text.
- Supplier names can be normalised enough to support ranking, trend, and white-space analysis.
- White-space views are based **only on historical awards** (no open tender or CRM data).

---

## 4. Core user questions

The product should help users answer:

### 4.1 Market overview

- “What is the total value of **medical-related** awards in the last 12 months?”
- “How has the public medical procurement spend changed since 2020?”

### 4.2 Buyers (agencies)

- “Which agencies spend the most on medical tenders overall?”
- “How has **Agency X**’s medical spend changed over time?”
- “Which agencies are most active in a specific subcategory (e.g. medical devices)?”

### 4.3 Suppliers

- “Who are the top suppliers by awarded amount in **my product area**?”
- “How has **Supplier Y**’s award value trended over the past few years?”

### 4.4 Competition

- “Who are the main competitors in **medical consumables**?”
- “Which suppliers often appear in similar tenders (same keywords / category)?”

### 4.5 Tender discovery

- “Show me tenders with `gloves` or `orthopedic` in the description with award amounts above $X.”
- “List recent tenders for `diagnostic equipment` and who won them.”

### 4.6 White space & expansion

- “Which agencies have **significant spend in my product category** but have **never awarded to my company**?”
- “For Supplier Y in diagnostics, which hospitals are big spenders in diagnostics but currently award to competitors instead?”
- “Rank white-space agencies by potential — total spend in my category, growth over time, and presence of key competitors.”

---

## 5. v1 feature set (analytics + AI assistant)

> **Note:** “v1” here refers to the first implementation of the product (including white space), not the older spec.

### 5.1 Dashboard – core analytics

**Filters:**

- Date range (from / to)
- Medical category (e.g. All Medical, Medical Devices, Consumables, Diagnostics, Services)
- Agency (optional)
- Supplier (optional)

**Components:**

1. **KPI cards**
   - Total awarded amount (S$)
   - Number of medical tenders
   - Number of unique buyers (agencies)
   - Number of unique suppliers

2. **Charts**
   - Line chart: medical award spend over time (monthly/quarterly)
   - Bar chart: top agencies by medical spend
   - Bar chart: top suppliers by medical spend

3. **Tables**
   - Top agencies (with spend, count of tenders)
   - Top suppliers (with spend, count of tenders)
   - Tender list:
     - Columns: award date, tender no, description (truncated), agency, supplier, award amount, category.

### 5.2 White-space analysis views

The white-space feature uses only award data to show **where a supplier is absent despite significant spend** in their category.

#### 5.2.1 Definitions

- **Reference supplier:** the supplier selected for analysis (e.g. “Supplier ABC”).
- **Relevant category:** medical category or keyword cluster, e.g. `Diagnostics`, `Medical Devices`, or a free-text keyword filter.
- **White-space agency:** an agency that:
  - Has **non-trivial spend** in the relevant category over the selected period (e.g. >= S$X threshold), and
  - Has **zero awards** to the reference supplier in that category over the same period.

#### 5.2.2 UX & components

New dashboard section: **“White-space opportunities”**.

Inputs:

- Supplier selector (single required).
- Category selector (required).
- Optional:
  - Minimum total spend threshold (e.g. default S$100k).
  - Lookback period (e.g. last 12 / 24 / 36 months).

Outputs:

1. **Summary KPIs**
   - Number of white-space agencies.
   - Total medical spend in the selected category by these agencies.
   - Share of total category spend that is currently “white space” for the supplier.

2. **White-space agency table**
   - Columns:
     - Agency
     - Total spend in selected category (S$) over period
     - Spend trend (e.g. simple % change vs previous period or indicator: Up / Flat / Down)
     - Top 1–3 competitor suppliers in that agency/category (by awarded amount)
     - Count of tenders in category
   - Sortable by total spend (default: descending).

3. **Agency detail drill-down (on row click)**
   - Time-series of agency spend in the selected category.
   - List of recent tenders in the category:
     - award date, tender no, description (truncated), winning supplier, award amount.

### 5.3 AI assistant / chatbot

Embedded on the dashboard page:

- Supports natural-language questions about:
  - Spend by category / agency / supplier.
  - Top N buyers / suppliers.
  - Recent tenders matching a certain keyword.
  - **White-space opportunities** for a given supplier/category.
- Uses **tool-based access** to the data:
  - Examples:
    - `get_category_summary`
    - `get_top_suppliers`
    - `search_tenders`
    - `get_whitespace_agencies(supplier, category, period, min_spend)`
- Returns:
  - Short textual answers.
  - Optionally structured data (e.g. a short table or list) rendered in UI.

Example supported questions:

- “For Supplier ABC in medical devices over the last 3 years, which agencies look like white-space opportunities?”
- “Show me the top 10 white-space agencies for Supplier XYZ in diagnostics in the last 24 months.”

---

## 6. Non-goals (explicitly out of scope for this version)

- No bidding recommendations (e.g. “You should bid $X to win”).
- No forecasting or predictive models (e.g. future spend predictions).
- No incorporation of private supplier CRM / internal sales data.
- No support for non-medical sectors (construction, ICT, etc.) beyond basic view.
- No pre-2020 data (unless additional sources are added later).
- No live open-tender pipeline from GeBIZ (only historical awards are used).

---

## 7. Quality & success criteria

### 7.1 Classification quality

- At least **80% accuracy** in manual review when deciding if a tender is **medical vs non-medical**.
- At least **70% accuracy** for subcategories (e.g. `medical_devices` vs `medical_consumables`).

Measured by manually sampling and reviewing a set (e.g. 100) of classified tenders.

### 7.2 White-space analysis quality

- Supplier name normalisation is good enough that:
  - The same supplier is not fragmented into many aliases for most real-world cases.
- Manual spot-checks for a few suppliers show:
  - White-space agencies truly have no recorded awards to that supplier in the category for the selected period.
  - Spend values and competitor lists match the underlying award records.

### 7.3 User experience

- Dashboard loads core data and charts within ~2–3 seconds for common queries.
- White-space views execute within a reasonable time (target: < 4 seconds for typical filters).
- Chatbot responses are:
  - Fact-based (no obvious hallucinations about numbers).
  - Able to answer common questions from the list in Section 4.

### 7.4 Technical robustness

- ETL can be re-run without manual intervention:
  - Idempotent based on `tender_no` and `award_date`.
- Data refresh process:
  - Can be scheduled (e.g. weekly) with clear documentation.

---

## 8. Technical overview (high-level)

- **Backend:**
  - Python (FastAPI)
  - Database: SQLite (prototype) or Postgres
  - Data ingestion:
    - CSV and/or data.gov.sg API
  - Business logic:
    - Classification of medical tenders.
    - Aggregation queries for dashboard and chatbot tools.
    - White-space computation:
      - Category-specific spend by agency.
      - Per-supplier award presence/absence by agency and category.

- **Frontend:**
  - React / Next.js (or equivalent)
  - Embeddable in Framer via iframe or link
  - Dedicated UI components for:
    - Filters.
    - KPI cards, charts, and tables.
    - White-space summary + table + drill-down.

- **AI assistant:**
  - OpenAI chat API
  - Tool-based approach, where the LLM calls backend functions instead of raw SQL.
  - Key tools include (names indicative):
    - `get_market_overview(params)`
    - `get_top_agencies(params)`
    - `get_top_suppliers(params)`
    - `search_tenders(params)`
    - `get_whitespace_agencies(params)`

---

## 9. Future extensions (post-v1 ideas)

> These are **not** in scope for this version but should be kept in mind for data model and API design.

- **Human-in-the-loop classification review UI**:
  - Admin interface to manually audit and correct tender classifications.
  - Use feedback to refine rules or train ML/LLM classifiers.

- **Recurring demand view** (pseudo-pipeline):
  - Identify agencies with consistent, repeating spend in similar categories or keywords.
  - E.g. “Agency X buys orthopedic implants every ~12–18 months”.

- **Renewal clock from award data**:
  - Infer potential contract durations from descriptions (“2-year term contract”, etc.).
  - Flag tenders whose implied contract period is approaching end as possible renewal opportunities.

- **Alerts:**
  - “Notify me when a new tender matches these keywords/categories.”
  - “Notify me when a new award appears in my category for Agency X.”

- **Comparative analytics:**
  - “Compare Supplier A vs Supplier B over the last 3 years.”

- **Additional data sources:**
  - Hospital groupings, more granular product taxonomies, or external healthcare market data.