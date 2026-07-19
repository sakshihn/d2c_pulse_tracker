# D2C Pulse Tracker

**A full-stack competitive pricing intelligence platform for Indian D2C beauty brands.**

Live pricing, price-history tracking, cross-brand product clustering, and analytics - built from scratch with Django, PostgreSQL, Celery, and applied ML/NLP.

---

## The Problem

Small and mid-sized D2C beauty brands don't have dedicated competitive intelligence teams. Founders and marketing leads end up manually checking competitor websites to answer basic questions: *Did a competitor drop their sunscreen price this week? What's a fair price point for a niacinamide serum? Which of our products are actually competing with which of theirs?*

That manual process doesn't scale, and it's easy to miss changes that matter.

**D2C Pulse Tracker automates this.** It continuously monitors real competitor pricing across four Indian D2C beauty brands, flags price changes as they happen, and groups similar products across brands — so instead of checking five websites by hand, a founder logs into one dashboard.

---

## What It Does

- **Scrapes live product data** from Plum Goodness, Minimalist, mCaffeine, and Dot & Key via their public Shopify storefronts
- **Cleans and normalizes messy real-world data** — inconsistent vendor naming, multi-variant pricing, promotional/freebie items mixed into real catalogs
- **Tracks price history over time** and automatically detects price changes using SQL window functions
- **Groups ~540 products into meaningful categories** (Sunscreen, Moisturizer, Body Wash, etc.) using a rule-based classifier, and separately explored TF-IDF + KMeans clustering for cross-brand product similarity
- **Runs on a schedule** via Celery + Celery Beat — no manual re-scraping needed
- **Secure multi-user access** — signup, login, and a real email notification sent on every login
- **Visual dashboard** — brand price comparisons, price-change alerts, category browsing, individual product price-history charts, and a 5-chart Insights page

---

## Tech Stack

| Layer | Tools |
|---|---|
| Backend | Django, PostgreSQL, Redis |
| Data Collection | Python `requests`, Shopify public product APIs |
| Automation | Celery + Celery Beat (scheduled scraping) |
| Data Science | SQL window functions (`LAG()`), TF-IDF + KMeans clustering, rule-based regex categorization |
| Auth & Email | Django auth (custom signup form), Gmail SMTP via Django signals |
| Frontend | Django templates, Chart.js, custom CSS |
| Infra | Docker Compose (Postgres + Redis), Git |

---

## Key Technical Decisions

- Used Shopify's public `/products.json` endpoint instead of HTML scraping — cleaner, more reliable, and avoids fragile parsing
- Built **per-brand data-cleaning logic**, since every brand tags promotional/freebie items differently (tag-based for some, title-pattern-based for others)
- Found and fixed a real multi-variant bug: some products have multiple size/shade variants, and early scraper logic only read the first variant — silently reporting wrong prices and stock status for products where variant `[0]` happened to be out of stock. Fixed by aggregating across all variants (lowest price, "any variant in stock" logic)
- Separated `Product` (current state) from `PriceHistory` (time-series snapshots) so price trends aren't lost on re-scrape
- Iterated on product categorization: started with TF-IDF/KMeans clustering, found it grouped by shared vocabulary rather than true product category (e.g. all "Vitamin C" products lumped together regardless of type) — switched to a rule-based classifier with carefully ordered regex rules for more reliable, explainable categories

---

## Coverage

~540 products across 4 brands, refreshed via scheduled scraping.

---

## Setup

```bash
git clone <your-repo-url>
cd d2c_pulse_tracker
cp .env.example .env   # fill in your own values
docker compose up -d   # starts Postgres + Redis
pip install -r requirements.txt
python manage.py migrate
python manage.py scrape_plum
python manage.py scrape_minimalist
python manage.py scrape_mcaffeine
python manage.py scrape_dotandkey
python manage.py categorize_products
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

To run automated scraping:
```bash
celery -A core worker --loglevel=info --pool=solo   # Windows
celery -A core beat --loglevel=info
```

---

## Screenshots
<img width="1917" height="858" alt="Screenshot 2026-07-19 114926" src="https://github.com/user-attachments/assets/7ce4419a-a4f7-4ce0-af67-04a4fd9d6048" />
<img width="1917" height="847" alt="Screenshot 2026-07-19 114944" src="https://github.com/user-attachments/assets/b3b4d2f4-ae6c-42eb-b5de-8b8d47648778" />
<img width="1240" height="698" alt="Screenshot 2026-07-19 114846" src="https://github.com/user-attachments/assets/831b9e47-ee50-4cf9-aa1a-83de550c17a8" />
<img width="1646" height="861" alt="Screenshot 2026-07-19 114807" src="https://github.com/user-attachments/assets/cde66aa3-384b-40a9-a9be-888d5ec85b6e" />
<img width="1431" height="855" alt="Screenshot 2026-07-19 114734" src="https://github.com/user-attachments/assets/93bf0d24-1fc2-450b-ac89-384721aa9a15" />
<img width="1432" height="852" alt="Screenshot 2026-07-19 114705" src="https://github.com/user-attachments/assets/5b99cd38-fc2f-43d4-b3ea-8646ec3b4757" />
<img width="1882" height="857" alt="Screenshot 2026-07-19 114549" src="https://github.com/user-attachments/assets/7ab7ad52-f680-409c-bb89-e4a5e0302c5c" />
<img width="1847" height="852" alt="Screenshot 2026-07-19 114356" src="https://github.com/user-attachments/assets/7cce2ebe-c3d6-41a1-8c20-73853a22d199" />
<img width="1602" height="850" alt="Screenshot 2026-07-19 115119" src="https://github.com/user-attachments/assets/955238d8-cc5a-4711-a7d6-8ace1b0175ea" />
<img width="1917" height="862" alt="Screenshot 2026-07-19 114905" src="https://github.com/user-attachments/assets/7092ef9e-01ff-4d94-b13b-02eba29ab8fa" />

---

## Future Improvements

- Real-time scraping frequency tuning based on brand catalog change rate
- Sentiment analysis on product reviews (not yet scraped)
- Expand to 8-10 brands for broader competitive coverage
- Deploy to a live server with continuous Celery Beat scheduling

---

With Love, Sakshi ❤️
