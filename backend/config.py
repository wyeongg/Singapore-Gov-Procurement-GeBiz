"""Centralised paths and constants for the project."""

from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).resolve().parent.parent

# Data paths
CSV_PATH = ROOT_DIR / "data" / "GovernmentProcurementviaGeBIZ.csv"
DB_PATH = ROOT_DIR / "data" / "processed" / "gebiz.db"

# ETL constants
EXPECTED_RAW_ROWS = 18_021
PLACEHOLDER_THRESHOLD = 999_999_999
