"""Data cleaning functions: date parsing, supplier normalisation, flagging."""

import pandas as pd

from backend.config import PLACEHOLDER_THRESHOLD


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse award_date (DD/MM/YYYY) → ISO 8601, add award_year & award_month."""
    parsed = pd.to_datetime(df["award_date"], format="%d/%m/%Y")
    df["award_date"] = parsed.dt.strftime("%Y-%m-%d")
    df["award_year"] = parsed.dt.year
    df["award_month"] = parsed.dt.month
    return df


def normalize_supplier(name: str) -> str:
    """UPPER, strip periods/commas, collapse whitespace."""
    name = name.upper()
    name = name.replace(".", "").replace(",", "")
    name = " ".join(name.split())
    return name.strip()


def normalize_suppliers(df: pd.DataFrame) -> pd.DataFrame:
    """Add supplier_name_norm column."""
    df["supplier_name_norm"] = df["supplier_name"].apply(normalize_supplier)
    return df


def flag_suspicious(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows with amounts >= PLACEHOLDER_THRESHOLD."""
    df["is_flagged"] = (df["awarded_amt"] >= PLACEHOLDER_THRESHOLD).astype(int)
    return df


def filter_valid_awards(df: pd.DataFrame) -> pd.DataFrame:
    """Remove 'Awarded to No Suppliers' rows."""
    return df[df["tender_detail_status"] != "Awarded to No Suppliers"].copy()
