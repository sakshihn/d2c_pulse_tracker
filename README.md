# D2C Pulse Tracker

A competitive intelligence tool that tracks pricing across Indian D2C beauty brands, built to help understand market positioning and detect price changes over time.

## Problem

Small/mid D2C beauty brands don't have dedicated competitive intelligence teams. This tool automates tracking of competitor pricing, surfaced as structured data instead of manual site-checking.

## What it does

- Scrapes product catalogs from Shopify-based D2C beauty brands (Plum Goodness, Minimalist, mCaffeine, Dot & Key)
- Cleans and normalizes inconsistent source data (vendor names, junk/promotional items)
- Tracks price history over time, enabling price-change detection
- Provides a filterable web view of all tracked products

## Tech stack

- **Backend**: Django, PostgreSQL, Redis
- **Data collection**: Python (`requests`), Shopify's public `/products.json` endpoint
- **Infrastructure**: Docker Compose (Postgres + Redis)
- **Analysis**: Raw SQL (window functions for price-change detection)

## Key technical decisions

- Used Shopify's public product API instead of HTML scraping where available (cleaner, more reliable data)
- Built per-brand junk-filtering logic, since each brand tags promotional/freebie items differently (tag-based, title-based)
- Separated `Product` (current state) from `PriceHistory` (time-series snapshots) to support trend analysis without losing historical data
- Data cleaning implemented at the source (in the scraper) rather than as a one-time SQL patch, to stay consistent across re-scrapes

## Current coverage

~540 products across 4 brands (Plum Goodness, Minimalist, mCaffeine, Dot & Key)

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in your own values
3. `docker compose up -d` (starts Postgres + Redis)
4. `pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py scrape_plum` (repeat for other brands)
7. `python manage.py runserver`
8. Visit `http://127.0.0.1:8000/products/`

## Future improvements

- Automated scheduled scraping via Celery
- Visual dashboard (price trend charts)
- Additional brand coverage
