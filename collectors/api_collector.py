
import httpx
import yaml
import hashlib
from datetime import datetime, timezone
from pathlib import Path

CONFIG = yaml.safe_load(open(Path(__file__).parent.parent / "config" / "sources.yaml"))

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def make_id(title, brand, drop_date):
    raw = f"{title.lower()}{brand.lower()}{drop_date}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def collect_ticketmaster(api_key: str) -> list:
    drops = []
    try:
        r = httpx.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params={
                "apikey": api_key,
                "classificationName": "music,sports",
                "sort": "date,asc",
                "size": 50,
                "countryCode": "US",
            },
            timeout=10,
        )
        events = r.json().get("_embedded", {}).get("events", [])
        for e in events:
            title    = e.get("name", "")
            date     = e.get("dates", {}).get("start", {}).get("dateTime", now_iso())
            url      = e.get("url", "")
            venue    = e.get("_embedded", {}).get("venues", [{}])[0].get("name", "")
            price_min = e.get("priceRanges", [{}])[0].get("min", 0) if e.get("priceRanges") else 0
            image_url = e.get("images", [{}])[0].get("url", "") if e.get("images") else ""
            drops.append({
                "id":          make_id(title, "Ticketmaster", date),
                "title":       title,
                "brand":       "Ticketmaster",
                "category":    "tickets",
                "subcategory": e.get("classifications", [{}])[0].get("segment", {}).get("name", ""),
                "drop_date":   date,
                "price":       float(price_min),
                "resell_est":  0.0,
                "url":         url,
                "image_url":   image_url,
                "source":      "api",
                "status":      "upcoming",
                "limited":     False,
                "notes":       f"Venue: {venue}",
                "found_at":    now_iso(),
            })
    except Exception as e:
        print(f"[ticketmaster] failed: {e}")
    return drops

def collect_seatgeek(client_id: str) -> list:
    drops = []
    try:
        r = httpx.get(
            "https://api.seatgeek.com/2/events",
            params={
                "client_id": client_id,
                "type":      "concert,sports,theater",
                "sort":      "datetime_local.asc",
                "per_page":  50,
            },
            timeout=10,
        )
        events = r.json().get("events", [])
        for e in events:
            title    = e.get("title", "")
            date     = e.get("datetime_utc", now_iso())
            url      = e.get("url", "")
            venue    = e.get("venue", {}).get("name", "")
            price    = e.get("stats", {}).get("lowest_price", 0) or 0
            drops.append({
                "id":          make_id(title, "SeatGeek", date),
                "title":       title,
                "brand":       "SeatGeek",
                "category":    "tickets",
                "subcategory": e.get("type", ""),
                "drop_date":   date,
                "price":       float(price),
                "resell_est":  0.0,
                "url":         url,
                "image_url":   e.get("performers", [{}])[0].get("image", "") if e.get("performers") else "",
                "source":      "api",
                "status":      "upcoming",
                "limited":     False,
                "notes":       f"Venue: {venue}",
                "found_at":    now_iso(),
            })
    except Exception as e:
        print(f"[seatgeek] failed: {e}")
    return drops

def collect_snkrs() -> list:
    """Nike SNKRS semi-public endpoint — no auth required."""
    drops = []
    try:
        r = httpx.get(
            "https://api.nike.com/launch/upcoming_products/3.0",
            params={
                "country":   "US",
                "language":  "en",
                "channelId": "d9a5bc42-4b9c-4976-858a-f159cf99c647",
            },
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        products = r.json().get("objects", [])
        for p in products:
            pub = p.get("productInfo", [{}])[0] if p.get("productInfo") else {}
            title    = pub.get("productContent", {}).get("fullTitle", p.get("copyDetails", {}).get("title", ""))
            date     = p.get("startEntryDate", p.get("stopEntryDate", now_iso()))
            price    = pub.get("launchView", {}).get("price", {}).get("currentRetail", 0) or 0
            url      = f"https://www.nike.com/launch/t/{p.get('slug', '')}"
            image_url = p.get("imageUrls", {}).get("productImageUrl", "")
            if not title:
                continue
            drops.append({
                "id":          make_id(title, "Nike SNKRS", date),
                "title":       title,
                "brand":       "Nike SNKRS",
                "category":    "sneakers",
                "subcategory": "jordan" if "jordan" in title.lower() else "nike",
                "drop_date":   date,
                "price":       float(price),
                "resell_est":  0.0,
                "url":         url,
                "image_url":   image_url,
                "source":      "api",
                "status":      "upcoming",
                "limited":     True,
                "notes":       "",
                "found_at":    now_iso(),
            })
    except Exception as e:
        print(f"[snkrs] failed: {e}")
    return drops

def run(tm_api_key="", sg_client_id="") -> list:
    drops = []
    drops += collect_snkrs()
    if tm_api_key:
        drops += collect_ticketmaster(tm_api_key)
    if sg_client_id:
        drops += collect_seatgeek(sg_client_id)
    return drops

if __name__ == "__main__":
    import os
    drops = run(
        tm_api_key=os.getenv("TICKETMASTER_KEY", ""),
        sg_client_id=os.getenv("SEATGEEK_ID", ""),
    )
    print(f"Collected {len(drops)} drops from APIs")
