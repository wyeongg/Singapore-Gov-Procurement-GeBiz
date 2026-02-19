"""FastAPI application — REST endpoints for the GeBIZ analytics dashboard.

Run from project root:
    uvicorn backend.api.main:app --reload
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.config import DB_PATH
from backend.services.analytics import (
    market_overview,
    spend_over_time,
    top_agencies,
    top_suppliers,
    search_tenders,
    subcategory_breakdown,
    whitespace_agencies,
)
from backend.api.chat import router as chat_router

app = FastAPI(
    title="GeBIZ Medical Procurement API",
    version="0.1.0",
)

# Allow frontend (React dev server) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@contextmanager
def get_db():
    """Yield a SQLite connection, closing it after use."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
    return {"status": "ok", "total_rows": count}


# ---------------------------------------------------------------------------
# Market overview KPIs
# ---------------------------------------------------------------------------

@app.get("/summary/market")
def api_market_overview(
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    with get_db() as conn:
        return market_overview(
            conn,
            medical_only=medical_only,
            category=category,
            date_from=date_from,
            date_to=date_to,
        )


# ---------------------------------------------------------------------------
# Spend over time
# ---------------------------------------------------------------------------

@app.get("/summary/spend-over-time")
def api_spend_over_time(
    period: str = "monthly",
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
):
    with get_db() as conn:
        return spend_over_time(
            conn,
            period=period,
            medical_only=medical_only,
            category=category,
            date_from=date_from,
            date_to=date_to,
            agency=agency,
        )


# ---------------------------------------------------------------------------
# Top agencies
# ---------------------------------------------------------------------------

@app.get("/summary/top-agencies")
def api_top_agencies(
    limit: int = 20,
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    with get_db() as conn:
        return top_agencies(
            conn,
            limit=limit,
            medical_only=medical_only,
            category=category,
            date_from=date_from,
            date_to=date_to,
        )


# ---------------------------------------------------------------------------
# Top suppliers
# ---------------------------------------------------------------------------

@app.get("/summary/top-suppliers")
def api_top_suppliers(
    limit: int = 20,
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
):
    with get_db() as conn:
        return top_suppliers(
            conn,
            limit=limit,
            medical_only=medical_only,
            category=category,
            date_from=date_from,
            date_to=date_to,
            agency=agency,
        )


# ---------------------------------------------------------------------------
# Tender search
# ---------------------------------------------------------------------------

@app.get("/tenders")
def api_search_tenders(
    keyword: Optional[str] = None,
    limit: int = 50,
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
    supplier: Optional[str] = None,
    min_amount: Optional[float] = None,
):
    with get_db() as conn:
        return search_tenders(
            conn,
            keyword=keyword,
            limit=limit,
            medical_only=medical_only,
            category=category,
            date_from=date_from,
            date_to=date_to,
            agency=agency,
            supplier=supplier,
            min_amount=min_amount,
        )


# ---------------------------------------------------------------------------
# Subcategory breakdown
# ---------------------------------------------------------------------------

@app.get("/summary/subcategories")
def api_subcategory_breakdown(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
):
    with get_db() as conn:
        return subcategory_breakdown(
            conn,
            date_from=date_from,
            date_to=date_to,
            agency=agency,
        )


# ---------------------------------------------------------------------------
# White-space analysis
# ---------------------------------------------------------------------------

@app.get("/whitespace/agencies")
def api_whitespace_agencies(
    supplier: str = Query(..., description="Supplier name (normalised)"),
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_spend: float = 100_000,
    limit: int = 50,
):
    with get_db() as conn:
        return whitespace_agencies(
            conn,
            supplier=supplier,
            category=category,
            date_from=date_from,
            date_to=date_to,
            min_spend=min_spend,
            limit=limit,
        )
