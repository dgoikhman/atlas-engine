"""Atlas Engine — Tier 0 pipeline, national scale.

Ingests ALL Zillow metros (top 250 by size with both value and rent data),
computes growth from Zillow's own price history, applies state-level factor
tables, attaches Census gazetteer coordinates, and emits
data/metros_live.csv in the same schema the site builder already reads.

Run:  python pipelines/public_data.py
Test: ZILLOW_LOCAL_DIR=data/test_fixtures python pipelines/public_data.py

Sources (all free):
  - Zillow Research ZHVI/ZORI metro CSVs (zillow.com/research/data/)
  - Census Gazetteer CBSA file (coordinates)
  - State factor tables below: property tax = state effective averages
    (Tax Foundation); landlord & climate = editorial state scores on public
    data (statute review + FEMA NRI direction), documented on /methodology/.
"""
import csv, io, os, sys, datetime, zipfile

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)

MAX_METROS = 250          # SizeRank cutoff
GROWTH_MONTHS = 60        # growth = 5-year ZHVI appreciation, percentiled

ZILLOW_URLS = {   # candidates tried in order; Zillow renames these occasionally
    "zhvi": [
        "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_month.csv",
    ],
    "zori": [
        "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_sa_month.csv",
        "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv",
        "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondo_sm_sa_month.csv",
    ],
}
GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_cbsa_national.zip"

# ---- State factor tables -------------------------------------------------
# landlord: 0-100 (eviction speed, rent control, statute lean) — editorial
# tax: effective property tax %, state average — Tax Foundation
# climate: 0-100 inverted risk (100 = low disaster/insurance pressure)
S = {
 "AL": (90, 0.40, 65), "AK": (75, 1.07, 70), "AZ": (85, 0.63, 75),
 "AR": (85, 0.62, 70), "CA": (35, 0.75, 55), "CO": (55, 0.51, 75),
 "CT": (45, 1.79, 80), "DE": (60, 0.59, 75), "FL": (80, 0.86, 40),
 "GA": (90, 0.90, 70), "HI": (50, 0.27, 60), "ID": (85, 0.67, 80),
 "IL": (35, 2.08, 85), "IN": (90, 0.84, 85), "IA": (85, 1.52, 80),
 "KS": (85, 1.34, 70), "KY": (80, 0.83, 75), "LA": (60, 0.56, 25),
 "ME": (55, 1.24, 85), "MD": (55, 1.05, 80), "MA": (40, 1.14, 80),
 "MI": (65, 1.38, 85), "MN": (60, 1.11, 80), "MS": (85, 0.67, 55),
 "MO": (85, 0.98, 75), "MT": (80, 0.74, 80), "NE": (85, 1.63, 75),
 "NV": (75, 0.59, 75), "NH": (65, 1.93, 85), "NJ": (40, 2.23, 75),
 "NM": (70, 0.67, 75), "NY": (30, 1.64, 80), "NC": (85, 0.80, 65),
 "ND": (85, 0.98, 80), "OH": (75, 1.52, 85), "OK": (90, 0.89, 60),
 "OR": (40, 0.93, 75), "PA": (70, 1.41, 90), "RI": (45, 1.40, 80),
 "SC": (85, 0.56, 60), "SD": (85, 1.17, 80), "TN": (90, 0.65, 70),
 "TX": (85, 1.68, 70), "UT": (85, 0.57, 80), "VT": (50, 1.83, 85),
 "VA": (75, 0.87, 80), "WA": (45, 0.87, 80), "WV": (75, 0.55, 80),
 "WI": (70, 1.61, 85), "WY": (85, 0.56, 80), "DC": (35, 0.57, 80),
}


def _read_csv(kind):
    local = os.environ.get("ZILLOW_LOCAL_DIR")
    if local:
        text = open(os.path.join(local, f"zillow_{kind}.csv")).read()
    else:
        text = None
        for url in ZILLOW_URLS[kind]:
            print(f"[zillow:{kind}] trying {url}")
            r = requests.get(url, timeout=180)
            if r.ok:
                text = r.content.decode("utf-8")
                break
            print(f"[zillow:{kind}] {r.status_code}, next candidate")
        if text is None:
            raise RuntimeError(f"no working {kind} URL — update ZILLOW_URLS from zillow.com/research/data/")
        open(os.path.join(RAW, f"zillow_{kind}.csv"), "w").write(text)
    rows = list(csv.DictReader(io.StringIO(text)))
    date_cols = sorted(c for c in rows[0] if c[:2] in ("19", "20") and "-" in c)
    return rows, date_cols


def _coords():
    """{(city_lower, state): (lat, lng)} from the Census CBSA gazetteer."""
    local = os.environ.get("ZILLOW_LOCAL_DIR")
    try:
        if local:
            text = open(os.path.join(local, "gazetteer.txt")).read()
        else:
            print(f"[gazetteer] {GAZ_URL}")
            r = requests.get(GAZ_URL, timeout=120)
            r.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(r.content))
            text = z.read(z.namelist()[0]).decode("utf-8", "replace")
    except Exception as e:
        print(f"[gazetteer] unavailable ({e}) — metros will miss map coords")
        return {}
    out = {}
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    reader.fieldnames = [f.strip() for f in reader.fieldnames]  # Census headers carry trailing spaces
    for row in reader:
        name = row.get("NAME", "")
        try:
            place, st = name.rsplit(",", 1)
            city = place.split("-")[0].strip().lower()
            st = st.replace("Metro Area", "").replace("Micro Area", "").strip()[:2]
            lat = float(row["INTPTLAT"]); lng = float(row["INTPTLONG"].strip())
            out.setdefault((city, st), (lat, lng))
        except (ValueError, KeyError):
            continue
    print(f"[gazetteer] {len(out)} CBSA coordinates")
    return out


def slugify(region, state):
    city = region.split(",")[0].split("-")[0].strip().lower()
    return "".join(c if c.isalnum() else "-" for c in city).strip("-") + "-" + state.lower()


def main():
    zhvi, zdates = _read_csv("zhvi")
    zori, rdates = _read_csv("zori")
    coords = _coords()
    latest_v, latest_r = zdates[-1], rdates[-1]
    back = zdates[-min(GROWTH_MONTHS, len(zdates) - 1) - 1]
    rents = {r["RegionID"]: r for r in zori}

    metros, growth_raw = [], []
    for row in zhvi:
        if str(row.get("RegionType", "")).lower() != "msa":
            continue
        try:
            if int(row.get("SizeRank", 99999)) > MAX_METROS:
                continue
        except ValueError:
            continue
        rrow = rents.get(row["RegionID"])
        v = row.get(latest_v); rent = rrow.get(latest_r) if rrow else None
        if not v or not rent:
            continue
        state = row["RegionName"].rsplit(",", 1)[-1].strip().upper()[:2]
        if state not in S:
            continue
        v, rent = float(v), float(rent)
        old = row.get(back)
        g = (v / float(old) - 1) if old and float(old) > 0 else None
        landlord, tax, climate = S[state]
        city_key = (row["RegionName"].split(",")[0].split("-")[0].strip().lower(), state)
        lat, lng = coords.get(city_key, ("", ""))
        metros.append({
            "slug": slugify(row["RegionName"], state),
            "name": row["RegionName"].split(",")[0].split("-")[0].strip(),
            "state": state, "lat": lat, "lng": lng,
            "home_value": round(v), "rent": round(rent),
            "landlord": landlord, "tax_rate": tax,
            "growth": g, "climate": climate, "blurb": "",
        })
        if g is not None:
            growth_raw.append(g)

    # growth -> percentile 0-100 within the cohort (data-driven, no editorial)
    growth_raw.sort()
    def pct(g):
        if g is None or not growth_raw:
            return 50
        below = sum(1 for x in growth_raw if x <= g)
        return round(below / len(growth_raw) * 100)
    seen, final = set(), []
    for m in metros:
        if m["slug"] in seen:
            continue
        seen.add(m["slug"])
        m["growth"] = pct(m["growth"])
        m["as_of"] = datetime.date.today().isoformat()
        final.append(m)

    min_rows = int(os.environ.get("MIN_METROS", "50"))
    if len(final) < min_rows:
        print(f"[error] only {len(final)} metros assembled — upstream format "
              "likely changed; not overwriting metros_live.csv")
        sys.exit(1)
    out_path = os.path.join(ROOT, "data", "metros_live.csv")
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(final[0].keys()))
        w.writeheader(); w.writerows(final)
    print(f"[done] {len(final)} metros -> {out_path} "
          f"(values {latest_v}, rents {latest_r}, growth vs {back})")


if __name__ == "__main__":
    main()
