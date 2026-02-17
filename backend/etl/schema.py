"""SQLite DDL for the tenders table."""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tenders (
    id                   INTEGER PRIMARY KEY,
    tender_no            TEXT    NOT NULL,
    tender_description   TEXT    NOT NULL,
    agency               TEXT    NOT NULL,
    award_date           TEXT    NOT NULL,
    award_year           INTEGER NOT NULL,
    award_month          INTEGER NOT NULL,
    tender_detail_status TEXT    NOT NULL,
    supplier_name        TEXT    NOT NULL,
    supplier_name_norm   TEXT    NOT NULL,
    awarded_amt          REAL    NOT NULL,
    is_medical           INTEGER NOT NULL DEFAULT 0,
    medical_subcategory  TEXT,
    classification_source TEXT,
    is_flagged           INTEGER NOT NULL DEFAULT 0
);
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_tenders_medical ON tenders(is_medical);",
    "CREATE INDEX IF NOT EXISTS idx_tenders_agency ON tenders(agency);",
    "CREATE INDEX IF NOT EXISTS idx_tenders_award_date ON tenders(award_date);",
    "CREATE INDEX IF NOT EXISTS idx_tenders_tender_no ON tenders(tender_no);",
    "CREATE INDEX IF NOT EXISTS idx_tenders_supplier_norm ON tenders(supplier_name_norm);",
    "CREATE INDEX IF NOT EXISTS idx_tenders_subcategory ON tenders(medical_subcategory);",
]
