<!-- docs/data-understanding.md -->

# Data Understanding – Government Procurement via GeBIZ

## 1. Dataset overview

- **Title:** Government Procurement via GeBIZ  
- **Publisher:** Ministry of Finance (MOF), Singapore  
- **Source:** data.gov.sg  
- **Dataset ID:** `d_acde1106003906a75c3fa052592f2fcb`  
- **Data coverage:** Apr 2020 – Mar 2025 (and updated periodically)  
- **File:** `GovernmentProcurementviaGeBIZ.csv` (~18K rows)  
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

## 5. Data quality questions / checks

During Phase 1 (ETL & EDA), we will specifically check:

1. **Nulls / missing values**
   - Presence of nulls in `award_date`, `awarded_amt`, `supplier_name`, `agency`.

2. **Duplicated identifiers**
   - Frequency of repeated `tender_no`.
   - Whether repeated `tender_no` rows represent multiple suppliers/items vs true duplicates.

3. **Supplier name consistency**
   - Variants like:
     - `ABC MEDICAL PTE LTD` vs `ABC MEDICAL PTE. LTD.`  
   - We may need simple normalisation (strip punctuation, upper-casing, etc.).

4. **Agency name consistency**
   - Different naming conventions for the same hospital / cluster.
   - Potential mapping table for agencies into higher-level groups (e.g. MOH, Hospital Cluster, Stat Board).

5. **Award amount anomalies**
   - Extremely large or zero values.
   - Multi-line tenders where the total value should be the **sum** of individual lines.

Results of these checks should be summarised and recorded here as we learn more.

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