# Client Insight Newsfeed – Design Note

## High-Level Architecture

The system follows a **linear ETL pipeline** with four layers:

```
JSON Input → Search & Scrape → LLM Enrichment → HTML Generation → Output Files
```

**Layer 1: Data Ingestion** (`setup.py`)
- Reads client JSON and groups by `companyId`
- Handles dynamic field mapping for flexibility

**Layer 2: News Discovery** (`scraper.py`)
- Executes targeted Google News searches using comprehensive keyword queries
- Includes rate-limiting (random 3-10 sec delays, 60 sec retry on 429 errors) to prevent HTTP 429 errors and IP blocks
- Falls back to broad search if targeted query yields no results

**Layer 3: LLM Enrichment** (`processor.py`)
- Uses OpenAI's `gpt-4o-mini` with structured output (Pydantic models)
- Context supplied: client name, title, description, date, media source
- Returns: headline, summary, why it matters (business opportunity), angle (conversation starter)

**Layer 4: HTML Rendering** (`generator.py`)
- Jinja2 template renders per-company newsfeed
- Includes client metadata, and news items with full enrichment
- One HTML file per company, saved to `output/`

**Main Orchestrator** (`main.py`)
- Chains all components, gracefully handles missing data and API errors
- Produces newsfeed only if news items are found

---

## Key Trade-offs & Constraints

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Search Strategy** | Broad keyword query (no complex operators) | Google News API limitations, simpler = more resilient |
| **Search Library** | `GoogleNews` (vs. `NewsAPI`, `SerpApi` or ChatGPT search) | `GoogleNews` is free to use but has rate constraints ($20 budget constraint), able to search all news not just global news |
| **LLM Model** | `gpt-4o-mini` (vs. `gpt-5`) | $20 budget constraint, sufficient for summarisation |
| **Output Format** | Static HTML (no database/API) | Simplicity, aligns with MVP scope |
| **Rate Limiting** | Client-side delays | Acceptable for ~100 clients, respects API terms, doesn't use $20 budget for searching |
| **Error Handling** | Soft failures (skip client, continue) | Prevents single failure from blocking entire run |
| **Optional Fields** | Website/address conditionally rendered | Gracefully handles incomplete client data |

---

## What Would Be Next Given More Time

1. **Scheduling & State**
   - Apache Airflow or Prefect for automated daily runs
   - Database (PostgreSQL) to track processed articles and user engagement

2. **Enriched UX**
   - Interactive dashboard with filtering/search
   - Sentiment analysis and priority scoring

3. **Advanced Search**
   - Broader data sources (e.g. Crunchbase, SEC filings)
   - Pay for the search to allow for faster processing and more encompassing data

4. **Cost Optimization**
   - Batch LLM calls + prompt caching
   - Switch to cheaper models for low-priority enrichment

---

## Summary

This solution delivers a clean, modular pipeline that meets all functional requirements within budget and scope constraints. The architecture prioritises reliability (graceful degradation) and maintainability (clear separation of concerns).
