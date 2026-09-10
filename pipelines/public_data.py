"""Atlas Engine — Tier 0 pipelines (free public downloads).

Run:  python pipelines/public_data.py
Output: data/metros_live.csv (same shape as data/seed_metros.csv, refreshed
values). site/build.py automatically prefers metros_live.csv when present.

Sources:
  - Zillow Research CSVs (ZHVI home values, ZORI rents), no key needed.
    URL patterns occasionally shift; update ZILLOW_URLS if a 404 appears:
    https://www.zillow.com/research/data/
  - Census ACS 5-year API (no key needed at low volume; add CENSUS_KEY env
    var if you hit limits): median household income per metro.
  - HUD Fair Market Rents API (token required, free at huduser.gov):
    skipped gracefully when HUD_TOKEN is unset.
"""
import csv, io, os, sys, datetime
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)

ZILLOW_URLS = {
    "zhvi": "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zori": "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondo_sm_sa_month.csv",
}

# Metros we track -> the RegionName prefix Zillow uses.
TRACKED = {
    "cleveland-oh": "Cleveland", "toledo-oh": "Toledo", "pittsburgh-pa": "Pittsburgh",
    "memphis-tn": "Memphis", "birmingham-al": "Birmingham", "detroit-mi": "Detroit",
    "tulsa-ok": "Tulsa", "oklahoma-city-ok": "Oklahoma City", "little-rock-ar": "Little Rock",
    "indianapolis-in": "Indianapolis", "kansas-city-mo": "Kansas City", "st-louis-mo": "St. Louis",
    "new-orleans-la": "New Orleans", "san-antonio-tx": "San Antonio", "huntsville-al": "Huntsville",
    "chicago-il": "Chicago", "austin-tx": "Austin", "denver-co": "Denver",
}


def fetch_zillow(kind: str) -> dict:
    """Return {slug: latest_value} for tracked metros from a Zillow CSV."""
    url = ZILLOW_URLS[kind]
    print(f"[zillow:{kind}] {url}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    open(os.path.join(RAW, f"zillow_{kind}.csv"), "wb").write(r.content)
    rows = list(csv.DictReader(io.StringIO(r.content.decode("utf-8"))))
    # Latest month = last date-like column.
    date_cols = [c for c in rows[0] if c[:2] in ("19", "20") and "-" in c]
    latest = sorted(date_cols)[-1]
    out = {}
    for row in rows:
        region = row.get("RegionName", "")
        for slug, prefix in TRACKED.items():
            if region.startswith(prefix) and row.get(latest):
                out[slug] = round(float(row[latest]))
    print(f"[zillow:{kind}] latest month {latest}, matched {len(out)} metros")
    return out


def fetch_census_income() -> dict:
    """Median household income (B19013) per tracked CBSA, ACS 5-year."""
    key = os.environ.get("CENSUS_KEY", "")
    url = ("https://api.census.gov/data/2023/acs/acs5?get=NAME,B19013_001E"
           "&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*")
    if key:
        url += f"&key={key}"
    print("[census] ACS B19013 for all CBSAs")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    data = r.json()
    out = {}
    for name, income, _ in data[1:]:
        for slug, prefix in TRACKED.items():
            if name.startswith(prefix) and income not in (None, "", "-666666666"):
                out[slug] = int(income)
    print(f"[census] matched {len(out)} metros")
    return out


def fetch_hud_fmr() -> dict:
    token = os.environ.get("HUD_TOKEN")
    if not token:
        print("[hud] HUD_TOKEN unset — skipping FMR (get a free token at huduser.gov)")
        return {}
    # Endpoint: https://www.huduser.gov/hudapi/public/fmr/data/{entityid}
    # Left as an exercise per metro CBSA code; wire when the token exists.
    return {}


def main():
    seed_path = os.path.join(ROOT, "data", "seed_metros.csv")
    metros = list(csv.DictReader(open(seed_path)))
    zhvi = fetch_zillow("zhvi")
    zori = fetch_zillow("zori")
    income = {}
    try:
        income = fetch_census_income()
    except Exception as e:
        print(f"[census] skipped ({e})")
    fetch_hud_fmr()

    today = datetime.date.today().isoformat()
    updated = 0
    for m in metros:
        slug = m["slug"]
        if slug in zhvi:
            m["home_value"] = str(zhvi[slug]); updated += 1
        if slug in zori:
            m["rent"] = str(zori[slug])
        if slug in income:
            m["median_income"] = str(income[slug])
        m["as_of"] = today

    out_path = os.path.join(ROOT, "data", "metros_live.csv")
    fieldnames = list(metros[0].keys())
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(metros)
    print(f"[done] {updated} metros refreshed -> {out_path}")
    if updated == 0:
        print("[warn] nothing matched — Zillow may have changed URL/columns; "
              "check https://www.zillow.com/research/data/ and update ZILLOW_URLS.")
        sys.exit(1)


if __name__ == "__main__":
    main()
