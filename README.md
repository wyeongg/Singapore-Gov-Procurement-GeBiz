# Singapore Medical Procurement Market Dashboard & AI Assistant

This project explores **Singapore public-sector procurement data** (via GeBIZ) and builds:

1. A **dashboard** to help medical suppliers understand:
   - Market size & trends
   - Top buying agencies
   - Top suppliers & competitors

2. An **AI assistant (chatbot)** that can answer natural-language questions about the same data.
---

## High-level architecture (planned)

Very roughly, the system will look like this:

```text
GeBIZ dataset (data.gov.sg)
          |
          v
    ETL / Ingestion (Python)
          |
          v
  Processed DB (SQLite / Postgres)
          |
          +---------------------+
          |                     |
          v                     v
   REST API (FastAPI)       Offline analysis / notebooks
          |
          v
+---------------------+-------------------------+
|   Dashboard (React) |   AI Chatbot (OpenAI)   |
+---------------------+-------------------------+