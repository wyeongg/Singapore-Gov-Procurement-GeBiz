"""Core analytics service layer.

All functions accept a sqlite3.Connection and return plain dicts/lists
ready to be serialised as JSON by a future API layer.

Filtering convention:
    - medical_only: if True, restrict to is_medical = 1
    - category: if provided, restrict to that medical_subcategory
    - date_from / date_to: ISO 8601 strings (YYYY-MM-DD), inclusive
    - agency: if provided, restrict to that agency name
    - supplier: if provided, restrict to that supplier_name_norm
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_where(
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
    supplier: Optional[str] = None,
) -> tuple[str, list]:
    """Build a WHERE clause and parameter list from common filters."""
    clauses = []
    params: list = []

    if medical_only:
        clauses.append("is_medical = 1")
    if category:
        clauses.append("medical_subcategory = ?")
        params.append(category)
    if date_from:
        clauses.append("award_date >= ?")
        params.append(date_from)
    if date_to:
        clauses.append("award_date <= ?")
        params.append(date_to)
    if agency:
        clauses.append("agency = ?")
        params.append(agency)
    if supplier:
        clauses.append("supplier_name_norm = ?")
        params.append(supplier)

    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return where, params


# ---------------------------------------------------------------------------
# 1. Market overview KPIs
# ---------------------------------------------------------------------------

def market_overview(
    conn: sqlite3.Connection,
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Return high-level KPIs for the dashboard header cards."""
    where, params = _build_where(
        medical_only=medical_only,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )
    row = conn.execute(
        f"""
        SELECT
            COALESCE(SUM(awarded_amt), 0)       AS total_awarded,
            COUNT(DISTINCT tender_no)            AS num_tenders,
            COUNT(DISTINCT agency)               AS num_agencies,
            COUNT(DISTINCT supplier_name_norm)   AS num_suppliers
        FROM tenders
        {where}
        """,
        params,
    ).fetchone()

    return {
        "total_awarded": row[0],
        "num_tenders": row[1],
        "num_agencies": row[2],
        "num_suppliers": row[3],
    }


# ---------------------------------------------------------------------------
# 2. Spend over time
# ---------------------------------------------------------------------------

def spend_over_time(
    conn: sqlite3.Connection,
    period: str = "monthly",
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return spend aggregated by time period.

    Args:
        period: 'monthly' or 'quarterly'
    """
    where, params = _build_where(
        medical_only=medical_only,
        category=category,
        date_from=date_from,
        date_to=date_to,
        agency=agency,
    )

    if period == "quarterly":
        group_expr = "award_year || '-Q' || ((award_month - 1) / 3 + 1)"
        order_expr = "award_year, (award_month - 1) / 3 + 1"
    else:  # monthly
        group_expr = "award_year || '-' || PRINTF('%02d', award_month)"
        order_expr = "award_year, award_month"

    rows = conn.execute(
        f"""
        SELECT
            {group_expr}                         AS period,
            COALESCE(SUM(awarded_amt), 0)        AS total_awarded,
            COUNT(DISTINCT tender_no)             AS num_tenders
        FROM tenders
        {where}
        GROUP BY {group_expr}
        ORDER BY {order_expr}
        """,
        params,
    ).fetchall()

    return [
        {"period": r[0], "total_awarded": r[1], "num_tenders": r[2]}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 3. Top agencies by spend
# ---------------------------------------------------------------------------

def top_agencies(
    conn: sqlite3.Connection,
    limit: int = 20,
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return agencies ranked by total awarded amount."""
    where, params = _build_where(
        medical_only=medical_only,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )
    params.append(limit)

    rows = conn.execute(
        f"""
        SELECT
            agency,
            COALESCE(SUM(awarded_amt), 0)        AS total_awarded,
            COUNT(DISTINCT tender_no)             AS num_tenders,
            COUNT(DISTINCT supplier_name_norm)    AS num_suppliers
        FROM tenders
        {where}
        GROUP BY agency
        ORDER BY total_awarded DESC
        LIMIT ?
        """,
        params,
    ).fetchall()

    return [
        {
            "agency": r[0],
            "total_awarded": r[1],
            "num_tenders": r[2],
            "num_suppliers": r[3],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 4. Top suppliers by spend
# ---------------------------------------------------------------------------

def top_suppliers(
    conn: sqlite3.Connection,
    limit: int = 20,
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return suppliers ranked by total awarded amount."""
    where, params = _build_where(
        medical_only=medical_only,
        category=category,
        date_from=date_from,
        date_to=date_to,
        agency=agency,
    )
    params.append(limit)

    rows = conn.execute(
        f"""
        SELECT
            supplier_name_norm,
            COALESCE(SUM(awarded_amt), 0)        AS total_awarded,
            COUNT(DISTINCT tender_no)             AS num_tenders,
            COUNT(DISTINCT agency)                AS num_agencies
        FROM tenders
        {where}
        GROUP BY supplier_name_norm
        ORDER BY total_awarded DESC
        LIMIT ?
        """,
        params,
    ).fetchall()

    return [
        {
            "supplier": r[0],
            "total_awarded": r[1],
            "num_tenders": r[2],
            "num_agencies": r[3],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 5. Search tenders
# ---------------------------------------------------------------------------

def search_tenders(
    conn: sqlite3.Connection,
    keyword: Optional[str] = None,
    limit: int = 50,
    medical_only: bool = True,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
    supplier: Optional[str] = None,
    min_amount: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Search and filter individual tender records."""
    where, params = _build_where(
        medical_only=medical_only,
        category=category,
        date_from=date_from,
        date_to=date_to,
        agency=agency,
        supplier=supplier,
    )

    if keyword:
        joiner = " AND " if where else " WHERE "
        where += joiner + "LOWER(tender_description) LIKE ?"
        params.append(f"%{keyword.lower()}%")

    if min_amount is not None:
        joiner = " AND " if where else " WHERE "
        where += joiner + "awarded_amt >= ?"
        params.append(min_amount)

    params.append(limit)

    rows = conn.execute(
        f"""
        SELECT
            tender_no,
            tender_description,
            agency,
            award_date,
            supplier_name,
            awarded_amt,
            medical_subcategory
        FROM tenders
        {where}
        ORDER BY award_date DESC
        LIMIT ?
        """,
        params,
    ).fetchall()

    return [
        {
            "tender_no": r[0],
            "description": r[1],
            "agency": r[2],
            "award_date": r[3],
            "supplier": r[4],
            "awarded_amt": r[5],
            "subcategory": r[6],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 6. Subcategory breakdown
# ---------------------------------------------------------------------------

def subcategory_breakdown(
    conn: sqlite3.Connection,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    agency: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return spend breakdown by medical subcategory."""
    where, params = _build_where(
        medical_only=True,
        date_from=date_from,
        date_to=date_to,
        agency=agency,
    )

    rows = conn.execute(
        f"""
        SELECT
            COALESCE(medical_subcategory, 'unclassified') AS subcategory,
            COALESCE(SUM(awarded_amt), 0)                 AS total_awarded,
            COUNT(DISTINCT tender_no)                      AS num_tenders
        FROM tenders
        {where}
        GROUP BY medical_subcategory
        ORDER BY total_awarded DESC
        """,
        params,
    ).fetchall()

    return [
        {"subcategory": r[0], "total_awarded": r[1], "num_tenders": r[2]}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 7. White-space analysis
# ---------------------------------------------------------------------------

def whitespace_agencies(
    conn: sqlite3.Connection,
    supplier: str,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_spend: float = 100_000,
    limit: int = 50,
) -> Dict[str, Any]:
    """Find agencies that spend in a category but have NOT awarded to a supplier.

    White-space = agencies with meaningful spend in the selected category
    that have zero awards to the reference supplier.

    Args:
        supplier: supplier_name_norm to check (the "reference supplier")
        category: medical_subcategory filter (optional)
        date_from / date_to: date range (optional)
        min_spend: minimum total spend threshold to qualify (default $100K)
        limit: max agencies to return

    Returns dict with:
        - summary: KPI totals (num white-space agencies, total spend, share)
        - agencies: list of white-space agencies with spend + top competitors
    """
    # Build base filters (always medical-only)
    where, params = _build_where(
        medical_only=True,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )

    # Step 1: total category spend across ALL agencies (for share calculation)
    total_category_spend = conn.execute(
        f"SELECT COALESCE(SUM(awarded_amt), 0) FROM tenders {where}",
        params,
    ).fetchone()[0]

    # Step 2: agencies the supplier HAS won in this category/period
    won_params = list(params) + [supplier]
    won_agencies = {
        row[0]
        for row in conn.execute(
            f"""
            SELECT DISTINCT agency FROM tenders
            {where}
            {"AND" if where else "WHERE"} supplier_name_norm = ?
            """,
            won_params,
        ).fetchall()
    }

    # Step 3: all agencies with spend >= min_spend in this category/period
    spend_params = list(params) + [min_spend]
    agency_rows = conn.execute(
        f"""
        SELECT
            agency,
            COALESCE(SUM(awarded_amt), 0)       AS total_spend,
            COUNT(DISTINCT tender_no)            AS num_tenders,
            COUNT(DISTINCT supplier_name_norm)   AS num_suppliers
        FROM tenders
        {where}
        GROUP BY agency
        HAVING total_spend >= ?
        ORDER BY total_spend DESC
        """,
        spend_params,
    ).fetchall()

    # Step 4: filter to only white-space agencies (not in won set)
    ws_agencies = []
    for row in agency_rows:
        if row[0] not in won_agencies:
            ws_agencies.append({
                "agency": row[0],
                "total_spend": row[1],
                "num_tenders": row[2],
                "num_suppliers": row[3],
            })

    # Step 5: for each white-space agency, get top 3 competitors
    for agency_info in ws_agencies[:limit]:
        comp_params = list(params) + [agency_info["agency"]]
        competitors = conn.execute(
            f"""
            SELECT supplier_name_norm, COALESCE(SUM(awarded_amt), 0) AS spend
            FROM tenders
            {where}
            {"AND" if where else "WHERE"} agency = ?
            GROUP BY supplier_name_norm
            ORDER BY spend DESC
            LIMIT 3
            """,
            comp_params,
        ).fetchall()
        agency_info["top_competitors"] = [
            {"supplier": c[0], "spend": c[1]} for c in competitors
        ]

    ws_agencies = ws_agencies[:limit]

    # Step 6: build summary
    ws_total_spend = sum(a["total_spend"] for a in ws_agencies)
    share = (ws_total_spend / total_category_spend * 100) if total_category_spend > 0 else 0

    return {
        "supplier": supplier,
        "category": category,
        "summary": {
            "num_whitespace_agencies": len(ws_agencies),
            "whitespace_total_spend": ws_total_spend,
            "category_total_spend": total_category_spend,
            "whitespace_share_pct": round(share, 1),
        },
        "agencies": ws_agencies,
    }
