"""Main ETL pipeline: CSV → clean → classify → SQLite.

Run from project root:
    python -m backend.etl.run_etl
"""

import os
import sqlite3

import pandas as pd

from backend.config import CSV_PATH, DB_PATH, EXPECTED_RAW_ROWS
from backend.etl.clean import (
    filter_valid_awards,
    flag_suspicious,
    normalize_suppliers,
    parse_dates,
)
from backend.etl.classify import classify_tender
from backend.etl.schema import CREATE_INDEXES_SQL, CREATE_TABLE_SQL


def run() -> None:
    # ------------------------------------------------------------------
    # 1. Load CSV
    # ------------------------------------------------------------------
    print(f"Loading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH, dtype={"_id": int, "awarded_amt": float})
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    assert len(df) == EXPECTED_RAW_ROWS, (
        f"Expected {EXPECTED_RAW_ROWS} rows, got {len(df)}"
    )

    # ------------------------------------------------------------------
    # 2. Filter out unusable rows
    # ------------------------------------------------------------------
    df = filter_valid_awards(df)
    print(f"  After filtering 'Awarded to No Suppliers': {len(df)} rows")

    # ------------------------------------------------------------------
    # 3. Parse dates
    # ------------------------------------------------------------------
    df = parse_dates(df)
    print(f"  Dates parsed: {df['award_date'].min()} → {df['award_date'].max()}")

    # ------------------------------------------------------------------
    # 4. Normalise supplier names
    # ------------------------------------------------------------------
    df = normalize_suppliers(df)

    # ------------------------------------------------------------------
    # 5. Flag suspicious amounts
    # ------------------------------------------------------------------
    df = flag_suspicious(df)
    n_flagged = df["is_flagged"].sum()
    print(f"  Flagged rows: {n_flagged}")

    # ------------------------------------------------------------------
    # 6. Classify medical / life-science
    # ------------------------------------------------------------------
    print("  Classifying tenders ...")
    results = df.apply(
        lambda row: classify_tender(row["tender_description"], row["agency"]),
        axis=1,
        result_type="expand",
    )
    df["is_medical"] = results[0].astype(int)
    df["medical_subcategory"] = results[1]
    df["classification_source"] = results[2]

    n_medical = df["is_medical"].sum()
    pct = n_medical / len(df) * 100
    print(f"  Medical rows: {n_medical} / {len(df)} ({pct:.1f}%)")

    # ------------------------------------------------------------------
    # 7. Rename _id → id for DB schema
    # ------------------------------------------------------------------
    df.rename(columns={"_id": "id"}, inplace=True)

    # Select columns in schema order
    columns = [
        "id", "tender_no", "tender_description", "agency",
        "award_date", "award_year", "award_month",
        "tender_detail_status", "supplier_name", "supplier_name_norm",
        "awarded_amt", "is_medical", "medical_subcategory",
        "classification_source", "is_flagged",
    ]
    df = df[columns]

    # ------------------------------------------------------------------
    # 8. Write to SQLite
    # ------------------------------------------------------------------
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS tenders")
    conn.execute(CREATE_TABLE_SQL)
    for idx_sql in CREATE_INDEXES_SQL:
        conn.execute(idx_sql)

    df.to_sql("tenders", conn, if_exists="append", index=False)
    conn.commit()
    print(f"\n  Database written to: {DB_PATH}")

    # ------------------------------------------------------------------
    # 9. Sanity checks
    # ------------------------------------------------------------------
    print("\n--- Sanity Checks ---")

    total = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
    print(f"Total rows: {total}")

    medical = conn.execute(
        "SELECT COUNT(*) FROM tenders WHERE is_medical = 1"
    ).fetchone()[0]
    print(f"Medical rows: {medical} ({medical / total * 100:.1f}%)")

    print("\nSubcategory breakdown:")
    rows = conn.execute(
        "SELECT COALESCE(medical_subcategory, 'unclassified'), COUNT(*) "
        "FROM tenders WHERE is_medical = 1 "
        "GROUP BY medical_subcategory ORDER BY COUNT(*) DESC"
    ).fetchall()
    for subcat, count in rows:
        print(f"  {subcat}: {count}")

    print("\nClassification source breakdown:")
    rows = conn.execute(
        "SELECT classification_source, COUNT(*) "
        "FROM tenders WHERE is_medical = 1 "
        "GROUP BY classification_source ORDER BY COUNT(*) DESC"
    ).fetchall()
    for source, count in rows:
        print(f"  {source}: {count}")

    flagged = conn.execute(
        "SELECT COUNT(*) FROM tenders WHERE is_flagged = 1"
    ).fetchone()[0]
    print(f"\nFlagged rows: {flagged}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    run()
