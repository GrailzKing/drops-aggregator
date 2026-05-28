
import feedparser
import yaml
import hashlib
import httpx
from datetime import datetime, timezone
from pathlib import Path

CONFIG = yaml.safe_load(open(Path(__file__).parent.parent / "config" / "sources.yaml"))

def make_id(title: str, brand: str, drop_date: str) -> str:
    raw = f"{title.lower()}{brand.lower()}{drop_date}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def collect_rss(sources: list, category: str) -> list:
    drops = []
    for src in sources:
        try:
            feed = feedparser.parse(src["url"])
            for entry in feed.entries[:20]:
                title = entry.get("title", "").strip()
                link  = entry.get("link", "")
                date  = entry.get("published", entry.get("updated", now_iso()))
                drops.append({
                    "id":          make_id(title, src["name"], date),
                    "title":       title,
                    "brand":       src["name"],
                    "category":    category,
                    "subcategory": "",
                    "drop_date":   date,
                    "price":       0.0,
                    "resell_est":  0.0,
                    "url":         link,
                    "image_url":   entry.get("media_thumbnail", [{}])[0].get("url", ""),
                    "source":      "rss",
                    "status":      "upcoming",
                    "limited":     any(kw in title.lower() for kw in ["limited", "exclusive", "signed", "autograph"]),
                    "notes":       "",
                    "found_at":    now_iso(),
                })
        except Exception as e:
            print(f"[rss] {src['name']} failed: {e}")
    return drops

def collect_shopify(sources: list, category: str) -> list:
    drops = []
    for src in sources:
        try:
            url = src["url"]
            if not url.endswith("products.json"):
                url = url.rstrip("/") + "/products.json"
            r = httpx.get(url, timeout=10, follow_redirects=True,
                          headers={"User-Agent": "Mozilla/5.0"})
            products = r.json().get("products", [])
            for p in products[:20]:
                title     = p.get("title", "").strip()
                handle    = p.get("handle", "")
                domain    = url.split("/collections")[0]
                link      = f"{domain}/products/{handle}"
                published = p.get("published_at", now_iso())
                price_str = p.get("variants", [{}])[0].get("price", "0")
                image_url = p.get("images", [{}])[0].get("src", "") if p.get("images") else ""
                drops.append({
                    "id":          make_id(title, src["name"], published),
                    "title":       title,
                    "brand":       src["name"],
                    "category":    category,
                    "subcategory": p.get("product_type", ""),
                    "drop_date":   published,
                    "price":       float(price_str),
                    "resell_est":  0.0,
                    "url":         link,
                    "image_url":   image_url,
                    "source":      "shopify",
                    "status":      "upcoming" if p.get("status") == "active" else "ended",
                    "limited":     any(kw in title.lower() for kw in ["limited", "exclusive", "collab", "drop"]),
                    "notes":       p.get("body_html", "")[:200],
                    "found_at":    now_iso(),
                })
        except Exception as e:
            print(f"[shopify] {src['name']} failed: {e}")
    return drops

def run() -> list:
    all_drops = []
    cats = CONFIG.get("music", {})
    all_drops += collect_rss(cats.get("rss", []), "music")
    all_drops += collect_shopify(cats.get("shopify", []), "music")

    cats = CONFIG.get("collectibles", {})
    all_drops += collect_shopify(cats.get("shopify_json", []), "collectibles")

    cats = CONFIG.get("sneakers", {})
    all_drops += collect_rss(cats.get("rss", []), "sneakers")
    all_drops += collect_shopify(cats.get("shopify_json", []), "sneakers")

    cats = CONFIG.get("streetwear", {})
    all_drops += collect_shopify(cats.get("shopify_json", []), "streetwear")

    cats = CONFIG.get("cards", {})
    all_drops += collect_rss(cats.get("rss", []), "cards")

    cats = CONFIG.get("tickets", {})
    all_drops += collect_rss(cats.get("rss", []), "tickets")

    cats = CONFIG.get("other", {})
    all_drops += collect_rss(cats.get("rss", []), "other")

    return all_drops

if __name__ == "__main__":
    drops = run()
    print(f"Collected {len(drops)} drops")
