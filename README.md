# SkillTrack PK 🇵🇰

A real-time data pipeline tracking what skills Pakistani companies are actually hiring for — updated daily.

## What it does
Scrapes live job listings from Rozee.pk across 20+ job categories, stores them in PostgreSQL, and transforms raw data into analytics-ready tables using dbt.

## Pipeline Architecture

## Tech Stack
- **Python + Playwright** — scraping & automation
- **PostgreSQL** — data storage
- **dbt** — data transformation
- **Power BI** — dashboard (coming soon)

## dbt Models
- `stg_jobs` — cleaned raw job listings
- `skill_counts` — most in-demand skills ranked by job count
- `company_activity` — hiring velocity per company
- `salary_by_role` — salary ranges by role and location

## Status
- [x] Scraper built and running
- [x] 472+ jobs ingested
- [x] dbt models live
- [ ] Power BI dashboard
- [ ] Auto-scheduling daily runs

## Data Source
Data sourced from Rozee.pk for educational purposes.
