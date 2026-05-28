
"""
Writes normalized drops to the Drops Aggregator Google Sheet.
Uses gspread with a service account JSON key stored as a GitHub Secret.
Tabs: Master + one per category. Appends new rows, skips known IDs.
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from schema import SHEET_HEADERS, SHEET_TABS

SHEET_ID   = "106og0wZRZcZOWmPGfuoUcCaYzz4bFyVszlWPrSqB1OU"
SCOPES     = ["https://www.googleapis.com/auth/spreadsheets"]

def get_client():
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON secret not set")
    info  = json.loads(creds_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)

def ensure_tabs(sh):
    existing = [ws.title for ws in sh.worksheets()]
    for tab in SHEET_TABS:
        if tab not in existing:
            ws = sh.add_worksheet(title=tab, rows=1000, cols=len(SHEET_HEADERS))
            ws.append_row(SHEET_HEADERS, value_input_option="RAW")
            print(f"[sheets] Created tab: {tab}")

def get_existing_ids(sh) -> set:
    """Read Master tab ID column to avoid duplicates."""
    ws  = sh.worksheet("Master")
    ids = ws.col_values(1)
    return set(ids[1:])  # skip header

def write_drops(drops: list):
    gc = get_client()
    sh = gc.open_by_key(SHEET_ID)
    ensure_tabs(sh)

    existing_ids = get_existing_ids(sh)
    new_drops    = [d for d in drops if d["id"] not in existing_ids]

    if not new_drops:
        print("[sheets] No new drops to write.")
        return

    master_ws = sh.worksheet("Master")
    rows_by_tab = {tab: [] for tab in SHEET_TABS}

    for drop in new_drops:
        row = [str(drop.get(h, "")) for h in SHEET_HEADERS]
        rows_by_tab["Master"].append(row)
        cat_tab = drop.get("category", "other").capitalize()
        if cat_tab in rows_by_tab:
            rows_by_tab[cat_tab].append(row)
        else:
            rows_by_tab["Other"].append(row)

    for tab, rows in rows_by_tab.items():
        if rows:
            ws = sh.worksheet(tab)
            ws.append_rows(rows, value_input_option="RAW")
            print(f"[sheets] +{len(rows)} rows → {tab}")

    print(f"[sheets] Done. {len(new_drops)} new drops written.")

if __name__ == "__main__":
    from collectors.rss_shopify_collector import run as rss_run
    from collectors.api_collector import run as api_run
    from processing.normalizer import process

    raw   = rss_run() + api_run()
    drops = process(raw)
    write_drops(drops)
