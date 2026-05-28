
# Schema for every drop record, regardless of source or category
# All collectors must normalize to this structure before writing to Sheets

DROP_SCHEMA = {
    "id": str,           # sha256 hash of (title + brand + drop_date) for dedup
    "title": str,        # product/event name
    "brand": str,        # Nike, Pokemon, Ticketmaster, etc.
    "category": str,     # music | collectibles | sneakers | streetwear | cards | tickets | other
    "subcategory": str,  # e.g. "signed", "funko", "jordan", "secret_lair"
    "drop_date": str,    # ISO 8601: 2026-06-01T10:00:00 or 2026-06-01 if time unknown
    "price": float,      # retail price, 0.0 if unknown
    "resell_est": float, # estimated resell value from enrichment, 0.0 if N/A
    "url": str,          # direct product/event URL
    "image_url": str,    # product image if available
    "source": str,       # collector that found it (rss | shopify | api | scrape | email)
    "status": str,       # upcoming | live | sold_out | ended
    "limited": bool,     # True if explicitly marked limited/exclusive
    "notes": str,        # any extra detail (presale code, signed, collab info)
    "found_at": str,     # ISO 8601 timestamp when collector found it
}

SHEET_TABS = [
    "Master",
    "Music",
    "Collectibles",
    "Sneakers",
    "Streetwear",
    "Cards",
    "Tickets",
    "Other",
]

SHEET_HEADERS = [
    "id", "title", "brand", "category", "subcategory",
    "drop_date", "price", "resell_est", "url", "image_url",
    "source", "status", "limited", "notes", "found_at"
]
