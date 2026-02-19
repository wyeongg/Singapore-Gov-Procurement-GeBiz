"""Chatbot service — Claude API with tool use for procurement analytics.

Wraps the existing analytics functions as Claude tools so the LLM can
answer natural-language questions about GeBIZ procurement data.
"""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Dict, List

import anthropic
from dotenv import load_dotenv

from backend.services.analytics import (
    market_overview,
    spend_over_time,
    top_agencies,
    top_suppliers,
    subcategory_breakdown,
    whitespace_agencies,
)

load_dotenv()

SYSTEM_PROMPT = """\
You are a Singapore government procurement analyst with access to the GeBIZ \
medical procurement database. The data covers April 2020 to March 2025 and \
includes 17,322 tender awards across 111 agencies and 6,083 suppliers. \
A subset of ~2,000 tenders are classified as medical/life-science.

Rules:
- ALWAYS use the provided tools to look up data. Never guess or make up numbers.
- Format currency in S$ with K/M/B suffixes (e.g., S$6.2B, S$450K).
- When listing items, use a markdown table for 3+ rows.
- Keep answers concise — 2-4 sentences for simple questions, tables for lists.
- The data only covers medical procurement by default (medical_only=True).
- Date parameters use ISO 8601 format (YYYY-MM-DD).
- Subcategories: diagnostics, devices, consumables, pharma_biotech, dental, \
services, general.
- Supplier names are normalised to uppercase (e.g., "BIOMED DIAGNOSTICS PTE LTD").
- If the user asks about something outside this dataset, say so politely.
"""

TOOLS = [
    {
        "name": "get_market_overview",
        "description": "Get high-level KPIs: total spend, number of tenders, agencies, and suppliers. Use this for summary/overview questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Medical subcategory filter (diagnostics, devices, consumables, pharma_biotech, dental, services, general). Omit for all.",
                },
                "date_from": {
                    "type": "string",
                    "description": "Start date (YYYY-MM-DD). Omit for no lower bound.",
                },
                "date_to": {
                    "type": "string",
                    "description": "End date (YYYY-MM-DD). Omit for no upper bound.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_spend_over_time",
        "description": "Get spend aggregated by time period (monthly or quarterly). Returns a time series of total spend and tender count per period.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["monthly", "quarterly"],
                    "description": "Aggregation period. Default: monthly.",
                },
                "category": {
                    "type": "string",
                    "description": "Medical subcategory filter.",
                },
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)."},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)."},
                "agency": {"type": "string", "description": "Filter to a specific agency."},
            },
            "required": [],
        },
    },
    {
        "name": "get_top_agencies",
        "description": "Get agencies ranked by total awarded amount. Returns agency name, total spend, tender count, and supplier count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of agencies to return. Default: 10.",
                },
                "category": {"type": "string", "description": "Medical subcategory filter."},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)."},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)."},
            },
            "required": [],
        },
    },
    {
        "name": "get_top_suppliers",
        "description": "Get suppliers ranked by total awarded amount. Returns supplier name, total spend, tender count, and agency count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of suppliers to return. Default: 10.",
                },
                "category": {"type": "string", "description": "Medical subcategory filter."},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)."},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)."},
                "agency": {"type": "string", "description": "Filter to a specific agency."},
            },
            "required": [],
        },
    },
    {
        "name": "search_tenders",
        "description": "Search individual tender records by keyword, agency, supplier, category, date range, or minimum amount. Returns tender details. Supplier and agency use partial matching (contain search), so you can use short names like 'PENTA-OCEAN' or 'Ministry of Health'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search term matched against tender description (case-insensitive).",
                },
                "limit": {"type": "integer", "description": "Max results. Default: 20."},
                "category": {"type": "string", "description": "Medical subcategory filter."},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)."},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)."},
                "agency": {
                    "type": "string",
                    "description": "Filter by agency (partial match, case-insensitive). E.g. 'Ministry of Health'.",
                },
                "supplier": {
                    "type": "string",
                    "description": "Filter by supplier name (partial match, case-insensitive). E.g. 'PENTA-OCEAN'.",
                },
                "min_amount": {
                    "type": "number",
                    "description": "Minimum awarded amount filter.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_subcategory_breakdown",
        "description": "Get spend breakdown by medical subcategory. Returns subcategory name, total spend, and tender count for each.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)."},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)."},
                "agency": {"type": "string", "description": "Filter to a specific agency."},
            },
            "required": [],
        },
    },
    {
        "name": "get_whitespace",
        "description": "Find white-space agencies — agencies that spend in a category but have NOT awarded tenders to a specific supplier. Use this for market opportunity analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "supplier": {
                    "type": "string",
                    "description": "Supplier name (normalised uppercase). REQUIRED.",
                },
                "category": {"type": "string", "description": "Medical subcategory filter."},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)."},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)."},
                "min_spend": {
                    "type": "number",
                    "description": "Minimum agency spend threshold. Default: 100000.",
                },
                "limit": {"type": "integer", "description": "Max agencies. Default: 20."},
            },
            "required": ["supplier"],
        },
    },
]


def _search_tenders_fuzzy(
    conn: sqlite3.Connection, tool_input: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Chat-specific tender search with LIKE matching for supplier and agency."""
    clauses = ["is_medical = 1"]
    params: list = []

    if tool_input.get("category"):
        clauses.append("medical_subcategory = ?")
        params.append(tool_input["category"])
    if tool_input.get("date_from"):
        clauses.append("award_date >= ?")
        params.append(tool_input["date_from"])
    if tool_input.get("date_to"):
        clauses.append("award_date <= ?")
        params.append(tool_input["date_to"])
    if tool_input.get("agency"):
        clauses.append("LOWER(agency) LIKE ?")
        params.append(f"%{tool_input['agency'].lower()}%")
    if tool_input.get("supplier"):
        clauses.append("LOWER(supplier_name_norm) LIKE ?")
        params.append(f"%{tool_input['supplier'].lower()}%")
    if tool_input.get("keyword"):
        clauses.append("LOWER(tender_description) LIKE ?")
        params.append(f"%{tool_input['keyword'].lower()}%")
    if tool_input.get("min_amount") is not None:
        clauses.append("awarded_amt >= ?")
        params.append(tool_input["min_amount"])

    where = " WHERE " + " AND ".join(clauses)
    limit = tool_input.get("limit", 20)
    params.append(limit)

    rows = conn.execute(
        f"""
        SELECT tender_no, tender_description, agency, award_date,
               supplier_name, awarded_amt, medical_subcategory
        FROM tenders {where}
        ORDER BY awarded_amt DESC
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


def execute_tool(
    tool_name: str, tool_input: Dict[str, Any], conn: sqlite3.Connection
) -> Any:
    """Dispatch a tool call to the matching analytics function."""
    if tool_name == "get_market_overview":
        return market_overview(
            conn,
            medical_only=True,
            category=tool_input.get("category"),
            date_from=tool_input.get("date_from"),
            date_to=tool_input.get("date_to"),
        )
    elif tool_name == "get_spend_over_time":
        return spend_over_time(
            conn,
            period=tool_input.get("period", "monthly"),
            medical_only=True,
            category=tool_input.get("category"),
            date_from=tool_input.get("date_from"),
            date_to=tool_input.get("date_to"),
            agency=tool_input.get("agency"),
        )
    elif tool_name == "get_top_agencies":
        return top_agencies(
            conn,
            limit=tool_input.get("limit", 10),
            medical_only=True,
            category=tool_input.get("category"),
            date_from=tool_input.get("date_from"),
            date_to=tool_input.get("date_to"),
        )
    elif tool_name == "get_top_suppliers":
        return top_suppliers(
            conn,
            limit=tool_input.get("limit", 10),
            medical_only=True,
            category=tool_input.get("category"),
            date_from=tool_input.get("date_from"),
            date_to=tool_input.get("date_to"),
            agency=tool_input.get("agency"),
        )
    elif tool_name == "search_tenders":
        return _search_tenders_fuzzy(conn, tool_input)
    elif tool_name == "get_subcategory_breakdown":
        return subcategory_breakdown(
            conn,
            date_from=tool_input.get("date_from"),
            date_to=tool_input.get("date_to"),
            agency=tool_input.get("agency"),
        )
    elif tool_name == "get_whitespace":
        return whitespace_agencies(
            conn,
            supplier=tool_input["supplier"],
            category=tool_input.get("category"),
            date_from=tool_input.get("date_from"),
            date_to=tool_input.get("date_to"),
            min_spend=tool_input.get("min_spend", 100_000),
            limit=tool_input.get("limit", 20),
        )
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def chat(
    messages: List[Dict[str, Any]], conn: sqlite3.Connection
) -> Dict[str, Any]:
    """Run a chat turn with Claude, handling tool use automatically.

    Args:
        messages: Conversation history [{role, content}, ...]
        conn: SQLite connection for analytics queries

    Returns:
        {reply: str, messages: [{role, content}, ...]}
        where messages is the updated conversation history
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # Work with a copy so we don't mutate the caller's list
    msgs = list(messages)

    # Tool-use loop: keep going until Claude gives a text response
    max_rounds = 5
    for _ in range(max_rounds):
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=msgs,
        )

        # Check if the response has any tool_use blocks
        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if response.stop_reason == "end_turn" or not tool_uses:
            # Extract the text reply
            text_parts = [b.text for b in response.content if b.type == "text"]
            reply = "\n".join(text_parts) if text_parts else ""
            msgs.append({"role": "assistant", "content": reply})
            return {"reply": reply, "messages": msgs}

        # Claude wants to use tools — add its response then execute each tool
        msgs.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in tool_uses:
            result = execute_tool(block.name, block.input, conn)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result, default=str),
            })

        msgs.append({"role": "user", "content": tool_results})

    # Safety fallback if max rounds exceeded
    fallback = "I needed more steps to answer that. Could you try a simpler question?"
    msgs.append({"role": "assistant", "content": fallback})
    return {"reply": fallback, "messages": msgs}
