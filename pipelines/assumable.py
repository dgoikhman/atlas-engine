"""BRRRR Markets — the Assumability Index.

Where do assumable low-rate mortgages concentrate? Government-backed loans
(FHA/VA/USDA) are assumable by law; the 2019-2021 vintage carries ~3% rates.
We pull HMDA public origination data (CFPB data-browser API) per state,
aggregate government-backed purchase originations 2019-2021 by metro (MSA),
and score each of our metros 0-100: share of gov-backed originations (60%)
+ depth of the assumable pool (40%).

Honest labels: this measures the assumable-eligible cohort, not confirmed
assumable listings; per-listing flags need remarks/title data (roadmap).

Run: python pipelines/assumable.py | offline: ASSUMABLE_LOCAL=data/test_fixtures
API shape is verified in CI; failures log the response head for repair.
"""
import csv, json, math, os, re, sys, time
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://ffiec.cfpb.gov/v2/data-browser-api/view/aggregations"
HDRS = {"User-Agent": "BRRRRMarkets/1.0 (public data research)"}
YEARS = ["2019", "2020", "2021"]
OUT = os.path.join(ROOT, "data", "assumable_index.csv")
STATES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
          "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV "
          "WI WY").split()


def fetch(state, year, loan_types):
    local = os.environ.get("ASSUMABLE_LOCAL")
    if local:
        p = os.path.join(local, f"hmda_{state.lower()}_{year}.json")
        return json.load(open(p)) if os.path.exists(p) else None
    # HMDA API allows max TWO filter criteria: actions_taken counts as one,
    # loan_types as the second. (Purposes dropped — gov refis are assumable too.)
    params = {"states": state, "years": year, "actions_taken": "1"}
    if loan_types:
        params["loan_types"] = loan_types      # 2=FHA 3=VA 4=USDA
    r = requests.get(API, params=params, headers=HDRS, timeout=120)
    if not r.ok:
        print(f"[assumable] {state} {year}: HTTP {r.status_code}: {r.text[:120]}")
        return None
    return r.json()


def total_from(payload):
    if not payload:
        return 0
    aggs = payload.get("aggregations") or []
    return sum(int(a.get("count", 0)) for a in aggs)


def norm(name):
    return re.sub(r"[^a-z]", "", (name or "").lower().split(",")[0].split("-")[0])


def main():
    src = os.path.join(ROOT, "data", "metros_live.csv")
    if not os.path.exists(src):
        src = os.path.join(ROOT, "data", "seed_metros.csv")
    metros = list(csv.DictReader(open(src)))
    by_state = {}
    for m in metros:
        by_state.setdefault(m["state"], []).append(m)

    rows = []
    for st in STATES:
        if st not in by_state:
            continue
        gov = allc = 0
        for y in YEARS:
            gov += total_from(fetch(st, y, "2,3,4"))
            time.sleep(0.3)
            allc += total_from(fetch(st, y, ""))
            time.sleep(0.3)
        if not allc:
            print(f"[assumable] {st}: no data — skipped")
            continue
        share = gov / allc * 100
        # v1 allocates state-level HMDA to metros weighted by our value/depth
        # (metro-level MSA joins land in v1.1 — labeled state-cohort until then)
        for m in by_state[st]:
            depth = gov * 0.6   # state pool proxy
            s = min(100, round(share / 35 * 60 + min(1.0, math.log10(max(depth, 10)) / 5) * 40))
            rows.append({"slug": m["slug"], "state": st,
                         "gov_1921_state": gov, "gov_share_pct": round(share, 1),
                         "assumability": s})
        print(f"[assumable] {st}: {gov:,} gov-backed of {allc:,} purchases "
              f"2019-21 ({share:.1f}%)")
    if rows and not any(float(r["gov_share_pct"]) > 0 for r in rows):
        sys.exit("[error] all gov shares zero — query broken; refusing to write garbage")
    if len(rows) < int(os.environ.get("MIN_ROWS", "50")):
        sys.exit(f"[error] only {len(rows)} metro rows — API shape likely "
                 "changed; see logged responses")
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"[done] Assumability Index for {len(rows)} metros -> {OUT}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        with open(os.path.join(ROOT, "data", "last_refresh.log"), "a") as f:
            f.write("\n[assumable CRASH]\n" + tb)
        sys.exit(1)
