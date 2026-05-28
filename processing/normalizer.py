
import hashlib
from datetime import datetime, timezone

DUPE_CACHE = set()

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def make_id(title: str, brand: str, drop_date: str) -> str:
    raw = f"{title.lower().strip()}{brand.lower().strip()}{drop_date}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def deduplicate(drops: list) -> list:
    seen = set()
    unique = []
    for drop in drops:
        key = drop.get("id") or make_id(drop["title"], drop["brand"], drop["drop_date"])
        if key not in seen:
            seen.add(key)
            unique.append(drop)
    return unique

def normalize(drop: dict) -> dict:
    """Ensure every field exists and is the right type."""
    defaults = {
        "id":          make_id(drop.get("title",""), drop.get("brand",""), drop.get("drop_date","")),
        "title":       "",
        "brand":       "",
        "category":    "other",
        "subcategory": "",
        "drop_date":   now_iso(),
        "price":       0.0,
        "resell_est":  0.0,
        "url":         "",
        "image_url":   "",
        "source":      "unknown",
        "status":      "upcoming",
        "limited":     False,
        "notes":       "",
        "found_at":    now_iso(),
    }
    for k, v in defaults.items():
        if k not in drop or drop[k] is None:
            drop[k] = v
    drop["price"]      = float(drop["price"] or 0)
    drop["resell_est"] = float(drop["resell_est"] or 0)
    drop["limited"]    = bool(drop["limited"])
    drop["title"]      = str(drop["title"]).strip()[:200]
    drop["notes"]      = str(drop["notes"]).strip()[:500]
    return drop

def process(drops: list) -> list:
    normalized = [normalize(d) for d in drops]
    unique     = deduplicate(normalized)
    unique.sort(key=lambda d: d.get("drop_date", ""))
    print(f"[normalizer] {len(drops)} in → {len(unique)} unique drops out")
    return unique
