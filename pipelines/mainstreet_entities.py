"""Main Street Atlas — Phase 2: row-level aged entities (Pro dataset).

Pulls individual aged businesses (20+ yrs, active) from the Colorado
registry: entity name, city, zip, formation date. Public records, row-level.

PRO-TIER DATA: outputs are .gitignored — they never land in the public
repo or on public pages. Delivery is Pro-only, under terms that require
business-channel outreach, honor the suppression list, and prohibit bulk
spam. See specs/main-street-atlas.md ("Contact rails").

Run:  python pipelines/mainstreet_entities.py           (full CO pull)
      MAX_ROWS=5000 python pipelines/mainstreet_entities.py   (sample)
"""
import csv, os, datetime, sys, time
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://data.colorado.gov/resource/4ykn-tg5h.json"
HDRS = {"User-Agent": "MainStreetAtlas/0.2 (public records research)"}
OUT = os.path.join(ROOT, "data", "pro", "mainstreet_entities.csv")
MAX_ROWS = int(os.environ.get("MAX_ROWS", "200000"))
PAGE = 25000


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    today = datetime.date.today()
    y20 = today.replace(year=today.year - 20).isoformat()
    where = ("entitystatus like 'Good Standing%' AND principalstate = 'CO' "
             f"AND entityformdate <= '{y20}T00:00:00.000'")
    rows, offset = [], 0
    while offset < MAX_ROWS:
        r = requests.get(API, params={
            "$select": "entityname,principalcity,principalzipcode,entityformdate,entityid",
            "$where": where, "$order": "entityid",
            "$limit": str(PAGE), "$offset": str(offset)}, headers=HDRS, timeout=120)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        for b in batch:
            fd = (b.get("entityformdate") or "")[:10]
            rows.append({
                "entity_id": b.get("entityid", ""),
                "name": (b.get("entityname") or "").strip(),
                "city": (b.get("principalcity") or "").strip().title(),
                "zip": (b.get("principalzipcode") or "")[:5],
                "formed": fd,
                "age_years": today.year - int(fd[:4]) if fd[:4].isdigit() else "",
            })
        offset += PAGE
        print(f"[entities] {len(rows)} rows...")
        time.sleep(0.5)
    if len(rows) < 1000 and MAX_ROWS > 5000:
        sys.exit(f"[error] only {len(rows)} rows — query or dataset changed")
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"[done] {len(rows)} aged CO entities -> {OUT} (gitignored, Pro-only)")


if __name__ == "__main__":
    main()
