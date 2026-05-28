
# Drops Aggregator

Automated collector for limited edition drops across music, collectibles, sneakers, streetwear, cards, tickets, and more.

## How it works
- GitHub Actions runs every 4 hours
- Collectors pull from RSS feeds, Shopify JSON endpoints, and public APIs
- Results are normalized, deduplicated, and written to a Google Sheet
- New drops only — existing IDs are skipped

## Setup (one-time)

### 1. Google Service Account
1. Go to console.cloud.google.com → New Project → "drops-aggregator"
2. Enable Google Sheets API
3. Create a Service Account → Download JSON key
4. Share your Google Sheet with the service account email (Editor access)
5. In GitHub repo → Settings → Secrets → add `GOOGLE_SERVICE_ACCOUNT_JSON` (paste the entire JSON)

### 2. Optional API keys (free tiers)
- `TICKETMASTER_KEY` — register at developer.ticketmaster.com (free)
- `SEATGEEK_ID` — register at seatgeek.com/api (free)
Add each as a GitHub Secret.

### 3. Run manually
Go to Actions tab → "Collect Drops" → Run workflow

## File structure
```
drops-aggregator/
├── .github/workflows/collect.yml   ← scheduler
├── collectors/
│   ├── rss_shopify_collector.py    ← RSS + Shopify feeds
│   └── api_collector.py            ← SNKRS, Ticketmaster, SeatGeek
├── processing/
│   └── normalizer.py               ← dedup + schema enforcement
├── outputs/
│   └── sheets_writer.py            ← Google Sheets writer
├── config/
│   └── sources.yaml                ← all source URLs (edit here to add sources)
├── schema.py                       ← shared data schema
└── requirements.txt
```

## Adding a new source
Open `config/sources.yaml` and add a URL under the right category and type (`rss`, `shopify_json`, `api`, or `scrape`). No code changes needed for RSS and Shopify sources.

## Google Sheet
[Drops Aggregator](https://docs.google.com/spreadsheets/d/106og0wZRZcZOWmPGfuoUcCaYzz4bFyVszlWPrSqB1OU/edit)
Tabs: Master · Music · Collectibles · Sneakers · Streetwear · Cards · Tickets · Other
