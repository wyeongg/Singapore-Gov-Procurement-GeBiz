<!-- docs/data-understanding.md -->

# Data Understanding – Government Procurement via GeBIZ

## 1. Dataset overview

- **Title:** Government Procurement via GeBIZ  
- **Publisher:** Ministry of Finance (MOF), Singapore  
- **Source:** data.gov.sg  
- **Dataset ID:** `d_acde1106003906a75c3fa052592f2fcb`  
- **Data coverage:** Apr 2020 – Mar 2025 (updated periodically)
- **File:** `GovernmentProcurementviaGeBIZ.csv` (18,021 rows incl. header)  
- **Licence:** Singapore Open Data Licence (free for personal & commercial use)

This dataset lists all open tenders put out by Singapore government agencies since FY2020, with award information at the tender level.

For this project, we will focus on **awarded tenders** and filter to **medical-related tenders** using a classification strategy defined separately.

---

## 2. Schema

### 2.1 Column dictionary

| Title                  | Column name            | Type    | Unit | Description                                           |
| ---------------------- | ---------------------- | ------- | ---- | ----------------------------------------------------- |
| Tender No              | `tender_no`           | Text    | –    | Unique identifier for the tender                      |
| Tender Description     | `tender_description`  | Text    | –    | Free-text description of the tender                   |
| Agency                 | `agency`              | Text    | –    | Government agency issuing the tender                  |
| Award Date             | `award_date`          | Text    | –    | Date when the tender was awarded                      |
| Tender Detail Status   | `tender_detail_status`| Text    | –    | Status of award details (e.g. “Awarded to Suppliers”) |
| Supplier Name          | `supplier_name`       | Text    | –    | Name of the awarded supplier                          |
| Awarded Amt            | `awarded_amt`         | Numeric | S$   | Award amount in Singapore dollars                     |

### 2.2 Initial data types (internal)

For internal processing (ETL), we will cast:

- `tender_no` → string
- `tender_description` → string (UTF-8)
- `agency` → string
- `award_date` → `date` (parse from `DD/MM/YYYY` or similar)
- `tender_detail_status` → string (categorical)
- `supplier_name` → string
- `awarded_amt` → decimal / float (S$)

---

## 3. Data semantics for this project

We treat each row as an **award record** with:

- One tender (`tender_no`)
- One supplier (`supplier_name`)
- One award amount (`awarded_amt`)
- One agency (`agency`)
- One award date (`award_date`)

Some tenders may have **multiple rows** (e.g. “Awarded by Items”) with different suppliers and/or amounts. Our analytics will handle this by aggregating at the appropriate level (per supplier, per agency, per time period).

Only tenders with a valid award status and non-null award amount will be counted in spend metrics.

---

## 4. Planned filters & business rules

These are the default rules we will apply in ETL / analytics:

1. **Award status filter**

   Include tenders where:

   - `tender_detail_status` is in:
     - `"Awarded to Suppliers"`
     - `"Awarded by Items"`
     - `"Award by interface record"`

   Exclude:

   - `"Awarded to No Suppliers"`  
   - Any null/unknown statuses

2. **Medical vs non-medical**

   - We will **not** use the entire dataset directly.
   - Instead, we classify tenders into:
     - `medical` vs `non_medical`
     - Optional subcategories (e.g. `medical_devices`, `medical_consumables`)
   - The classification logic is defined in `medical-classification-strategy.md`.

3. **Time range**

   - Default analysis: Apr 2020 → latest available award date.
   - Dashboard filters will allow custom date ranges.

---

## 5. Data quality findings

> EDA performed on full CSV (18,021 rows) — Feb 2025.

### 5.1 Nulls / missing values

**Zero nulls across all 8 columns.** No empty strings or whitespace-only values. The dataset is fully populated.

### 5.2 Date range & format

- **Format:** `DD/MM/YYYY` — all rows parseable, zero failures.
- **Range:** 01 Apr 2020 → 28 Mar 2025.
- **Year distribution:** 2020: 2,450 | 2021: 3,969 | 2022: 3,464 | 2023: 3,717 | 2024: 3,511 | 2025: 910.

### 5.3 Tender detail status

| Status | Count | % |
|---|---|---|
| Awarded to Suppliers | 9,174 | 50.9% |
| Awarded by Items | 7,590 | 42.1% |
| Awarded to No Suppliers | 699 | 3.9% |
| Award by interface record | 558 | 3.1% |

The 699 "Awarded to No Suppliers" rows have `supplier_name = "Unknown"` and `awarded_amt = 0`. These should be **excluded** from spend analytics.

### 5.4 Tender number duplicates

- **11,915 unique `tender_no`** across 18,021 rows (avg 1.51 rows per tender).
- 10,264 tenders (86%) have exactly 1 row (single supplier award).
- 763 tenders have 2 rows, 285 have 3, tapering off after that.
- Largest: `FINVITETT20300009` (131 rows), `FINVITETT23000006` (127 rows), `ITA000ETT21000007` (108 rows) — these are framework/panel contracts with many suppliers.
- **Conclusion:** multi-row tenders are real (multi-supplier awards), not true duplicates. Aggregate by summing where needed.

### 5.5 Award amount distribution

| Stat | Value |
|---|---|
| Min | $0.00 |
| Max | $1,493,179,167 |
| Mean | $6,100,677 |
| Median | $170,920 |
| Std Dev | $41,205,647 |
| 25th pctl | $7,490 |
| 75th pctl | $893,000 |
| 90th pctl | $5,157,000 |
| 99th pctl | $154,157,600 |

- **Heavily right-skewed** — mean ($6.1M) is ~36x the median ($171K).
- **703 zero values** — all correspond to "Awarded to No Suppliers" status.
- **0 negative values.**
- **245 rows > $100M** — dominated by large infrastructure (LTA MRT projects, PUB water plants, MHA checkpoint construction, NEA waste management).

**Notable outliers:**
- $1,493,179,167 — Keppel Seghers / NEA Integrated Waste Management Facility.
- $999,999,999 — Chye Thiam Maintenance / NEA public cleaning — likely a placeholder/cap value, warrants investigation.

### 5.6 Agency names

- **111 unique agencies.**
- Top 5 by row count: HDB (1,283), A*STAR (877), People's Association (829), PUB (814), LTA (702).
- Top 20 agencies account for ~60% of rows.
- No obvious inconsistencies detected (e.g. no duplicate agency names with minor spelling differences).

### 5.7 Supplier names

- **6,083 unique suppliers.**
- Top supplier is "Unknown" (699 rows) — the "Awarded to No Suppliers" records.
- Next: NCS PTE. LTD. (172), WSH EXPERTS PTE. LTD. (120), KPMG (96), Ernst & Young (79).
- **~7 name variant groups detected** with minor punctuation/casing differences (e.g. `"IRADAR SDN. BHD."` vs `"IRADAR SDN BHD"`, `"Advancedata Network Sdn Bhd"` vs `"ADVANCEDATA NETWORK SDN. BHD."`).
- Overall supplier names are **reasonably clean** — simple normalisation (strip periods, uppercase) should handle most variants.

### 5.8 ETL implications

1. **Exclude** rows where `tender_detail_status = "Awarded to No Suppliers"` (699 rows, all zero-amount with supplier "Unknown").
2. **Parse** `award_date` as `DD/MM/YYYY` → date type.
3. **Cast** `awarded_amt` to float (already numeric, no parsing issues).
4. **Normalise** `supplier_name`: strip periods, standardise casing, trim whitespace.
5. **Flag** the $999,999,999 row for manual review (possible placeholder value).
6. After exclusions, **working dataset = ~17,322 rows** with valid awards.

---

## 6. Intended usage in this project

This dataset will underpin:

- A **dashboard** that shows:
  - Market size and trends for medical-related tenders.
  - Top buyers (agencies) and suppliers.
  - Drill-down into tenders by category, agency, and supplier.

- An **AI assistant / chatbot** that:
  - Answers natural-language questions about public-sector medical procurement.
  - Uses controlled tools/functions to query this dataset (not free-form SQL from users).

Any additional external data sources (e.g. manual mapping tables for hospitals, product taxonomies) will be documented separately.

---

## 7. White-space analysis — assumptions & limitations

The white-space feature identifies agencies that **spend in a supplier's category** but have **never awarded to that supplier**. It is implemented in `backend/services/analytics.py` → `whitespace_agencies()`.

### Assumptions

1. **Historical awards only.** White-space is inferred purely from past award records. There is no open-tender pipeline, CRM data, or bid history.
2. **Supplier identity relies on `supplier_name_norm`.** If a supplier operates under multiple legal entities not caught by normalization, their awards may appear fragmented, producing false white-space.
3. **Category is based on `medical_subcategory`.** Subcategory assignment uses the ETL classification (keyword + bigram + agency). Misclassified tenders can distort results (e.g. hospital construction inflating "dental").
4. **Minimum spend threshold** (default $100K) filters out agencies with trivial spend to focus on meaningful opportunities.
5. **No contract duration awareness.** A large one-off award (e.g. 3-year contract) appears the same as recurring annual spend. Renewal timing is not modelled.

### Known limitations

- **Hospital/infrastructure construction** tenders classified as medical inflate spend figures for certain agencies (e.g. MOH HQ $4.3B includes building projects). These are technically healthcare spending but not procurement opportunities for medical device/reagent suppliers.
- **Agency merges/renames** are not tracked. If an agency was renamed during the data period, old and new names appear as separate agencies.
- **Consortium or subcontracted awards** are not decomposed — only the prime awardee appears.