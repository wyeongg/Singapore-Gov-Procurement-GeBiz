<!-- docs/product-spec-v1.md -->

# Product Spec – Singapore Medical Procurement Market Dashboard & AI Assistant (v1)

## 1. Overview

We are building a **web-based dashboard and AI assistant** for medical suppliers interested in Singapore public-sector procurement opportunities.

The product ingests the **Government Procurement via GeBIZ** dataset (Apr 2020 onwards) and focuses on **medical-related tenders**. It presents structured analytics and lets users ask free-text questions via an OpenAI-powered chatbot.

---

## 2. Target users & persona

### Primary persona

- Role: Business development / sales manager, founder, or strategic planner at a **medical supplier** (devices, consumables, diagnostics, services).
- Goal: Understand **who buys what**, **who wins**, and **how big the opportunity is** in Singapore’s public sector.

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
- Supplier names can be normalised enough to support ranking and trend analysis.

---

## 4. Core user questions (v1)

The product should help users answer:

### Market overview

- “What is the total value of **medical-related** awards in the last 12 months?”
- “How has the public medical procurement spend changed since 2020?”

### Buyers (agencies)

- “Which agencies spend the most on medical tenders overall?”
- “How has **Agency X**’s medical spend changed over time?”
- “Which agencies are most active in a specific subcategory (e.g. medical devices)?”

### Suppliers

- “Who are the top suppliers by awarded amount in **my product area**?”
- “How has **Supplier Y**’s award value trended over the past few years?”

### Competition

- “Who are the main competitors in **medical consumables**?”
- “Which suppliers often appear in similar tenders (same keywords / category)?”

### Tender discovery

- “Show me tenders with `gloves` or `orthopedic` in the description with award amounts above $X.”
- “List recent tenders for `diagnostic equipment` and who won them.”

---

## 5. v1 feature set

### 5.1 Dashboard

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

### 5.2 AI assistant / chatbot

Embedded on the dashboard page:

- Supports natural-language questions about:
  - Spend by category / agency / supplier.
  - Top N buyers / suppliers.
  - Recent tenders matching a certain keyword.
- Uses **tool-based access** to the data:
  - e.g. `get_category_summary`, `get_top_suppliers`, `search_tenders`.
- Returns:
  - Short textual answers.
  - Optionally structured data (e.g. a short table or list) rendered in UI.

---

## 6. Non-goals (explicitly out of scope for v1)

- No bidding recommendations (e.g. “You should bid $X to win”).
- No forecasting or predictive models (e.g. future spend predictions).
- No incorporation of private supplier CRM / internal sales data.
- No support for non-medical sectors (construction, ICT, etc.) beyond basic view.
- No pre-2020 data (unless additional sources are added later).

---

## 7. Quality & success criteria

### 7.1 Classification quality

- At least **80% accuracy** in manual review when deciding if a tender is **medical vs non-medical**.
- At least **70% accuracy** for subcategories (e.g. `medical_devices` vs `medical_consumables`).

This will be measured by manually sampling and reviewing a set (e.g. 100) of classified tenders.

### 7.2 User experience

- Dashboard loads core data and charts within ~2–3 seconds for common queries.
- Chatbot responses are:
  - Fact-based (no obvious hallucinations about numbers).
  - Able to answer common questions from the list in Section 4.

### 7.3 Technical robustness

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
    - Classification of medical tenders
    - Aggregation queries for dashboard and chatbot tools

- **Frontend:**
  - React / Next.js (or equivalent)
  - Embeddable in Framer via iframe or link

- **AI assistant:**
  - OpenAI chat API
  - Tool-based approach, where the LLM calls backend functions instead of raw SQL

---

## 9. Future extensions (post-v1 ideas)

- LLM-based classification of tenders into detailed medical subcategories.
- Alerts:
  - “Notify me when a new tender matches these keywords/categories.”
- Comparative analytics:
  - “Compare Supplier A vs Supplier B over the last 3 years.”
- Additional data sources:
  - Hospital groupings, more granular product taxonomies, or external healthcare market data.