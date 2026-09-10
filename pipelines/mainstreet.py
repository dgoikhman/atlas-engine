"""Main Street Atlas — succession pipeline v0.1 (Colorado registry).

City-level aggregates from the Colorado Secretary of State business registry
via the state's open-data (Socrata) API — no bulk downloads, no scraping:
three aggregate queries return, per city, the count of active entities and
how many have been registered 20+ and 30+ years. Emits
data/mainstreet_cities.csv; the site renders /businesses/ pages from it.

Run:  python pipelines/mainstreet.py
Test: MAINSTREET_LOCAL=data/test_fixtures python pipelines/mainstreet.py

Legal note: public registry facts (filing dates, status, city), aggregated.
No owner names, no individual businesses at this phase. Florida/TX/WA join
in the scale phase (bulk-file parsing — see specs/main-street-atlas.md).
"""
import csv, json, os, sys, datetime
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Colorado business entities dataset (Socrata). If the resource id changes,
# find the current one at data.colorado.gov (search "business entities").
API = "https://data.colorado.gov/resource/4ykn-tg5h.json"
HDRS = {"User-Agent": "MainStreetAtlas/0.1 (public records research)"}
MIN_CITIES = int(os.environ.get("MIN_CITIES", "20"))


def q(where, name):
    local = os.environ.get("MAINSTREET_LOCAL")
    if local:
        return json.load(open(os.path.join(local, f"ms_{name}.json")))
    params = {
        "$select": "upper(principalcity) as city, count(1) as n",
        "$where": where,
        "$group": "upper(principalcity)",
        "$order": "n DESC",
        "$limit": "400",
    }
    r = requests.get(API, params=params, headers=HDRS, timeout=120)
    if not r.ok:
        print(f"[mainstreet] {name}: HTTP {r.status_code}: {r.text[:200]}")
        r.raise_for_status()
    return r.json()


def main():
    today = datetime.date.today()
    y20 = today.replace(year=today.year - 20).isoformat()
    y30 = today.replace(year=today.year - 30).isoformat()
    base = "entitystatus like 'Good Standing%' AND principalstate = 'CO'"
    total = q(base, "total")
    o20 = q(base + f" AND entityformdate <= '{y20}T00:00:00.000'", "over20")
    o30 = q(base + f" AND entityformdate <= '{y30}T00:00:00.000'", "over30")

    def m(rows):
        return {r["city"].strip(): int(r["n"]) for r in rows
                if r.get("city") and len(r["city"].strip()) > 2}
    T, A, B = m(total), m(o20), m(o30)

    rows = []
    for city, n in T.items():
        if n < 500:          # keep cities with real business bases
            continue
        rows.append({
            "slug": "".join(c if c.isalnum() else "-" for c in city.lower()).strip("-") + "-co",
            "city": city.title(), "state": "CO",
            "total_active": n,
            "over20": A.get(city, 0), "over30": B.get(city, 0),
            "share20": round(A.get(city, 0) / n * 100, 1),
            "share30": round(B.get(city, 0) / n * 100, 1),
            "as_of": today.isoformat(),
        })
    rows.sort(key=lambda r: -r["total_active"])
    rows = rows[:60]

    if len(rows) < MIN_CITIES:
        print(f"[error] only {len(rows)} cities assembled — dataset id or "
              "field names likely changed at data.colorado.gov; not writing")
        sys.exit(1)
    out = os.path.join(ROOT, "data", "mainstreet_cities.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"[done] mainstreet: {len(rows)} CO cities -> {out}")


if __name__ == "__main__":
    main()
