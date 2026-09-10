"""Atlas Engine — metro living-context pipeline (Census ACS).

Pulls, per metro: population + 5-year trend, median household income, and
the industry employment mix (13 sectors, % of workforce). Emits
data/metro_context.csv keyed by the same slugs as metros_live.csv; the site
builder renders /rentals/<slug>/living/ pages only for rows present here.

Run:  python pipelines/context.py            (CI / live)
Test: CONTEXT_LOCAL=data/test_fixtures python pipelines/context.py

Source: Census ACS 5-year Data Profiles (no key needed at this volume;
set CENSUS_KEY to raise limits). Population trend compares the 2023 and
2018 5-year vintages.
"""
import csv, json, os, sys
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSA = "metropolitan%20statistical%20area/micropolitan%20statistical%20area"
IND_FIELDS = {
    "DP03_0033PE": "Agriculture & mining", "DP03_0034PE": "Construction",
    "DP03_0035PE": "Manufacturing", "DP03_0036PE": "Wholesale trade",
    "DP03_0037PE": "Retail trade", "DP03_0038PE": "Transportation & utilities",
    "DP03_0039PE": "Information", "DP03_0040PE": "Finance, insurance & real estate",
    "DP03_0041PE": "Professional & management", "DP03_0042PE": "Education & health care",
    "DP03_0043PE": "Arts, food & hospitality", "DP03_0044PE": "Other services",
    "DP03_0045PE": "Public administration",
}


def _get(year, fields):
    local = os.environ.get("CONTEXT_LOCAL")
    if local:
        return json.load(open(os.path.join(local, f"acs_{year}.json")))
    key = os.environ.get("CENSUS_KEY", "")
    url = (f"https://api.census.gov/data/{year}/acs/acs5/profile"
           f"?get=NAME,{','.join(fields)}&for={MSA}:*")
    if key:
        url += f"&key={key}"
    print(f"[census] ACS {year} profile")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.json()


def _index(data, fields):
    """{(city_lower, state): {field: value}} keyed like the gazetteer."""
    head = data[0]
    out = {}
    for row in data[1:]:
        d = dict(zip(head, row))
        name = d.get("NAME", "")
        try:
            place, rest = name.rsplit(",", 1)
            city = place.split("-")[0].strip().lower()
            st = rest.replace("Metro Area", "").replace("Micro Area", "").strip()[:2]
        except ValueError:
            continue
        out.setdefault((city, st), {f: d.get(f) for f in fields})
    return out


def main():
    metros_path = os.path.join(ROOT, "data", "metros_live.csv")
    if not os.path.exists(metros_path):
        metros_path = os.path.join(ROOT, "data", "seed_metros.csv")
    metros = list(csv.DictReader(open(metros_path)))

    now_fields = ["DP05_0001E", "DP03_0062E"] + list(IND_FIELDS)
    cur = _index(_get(2023, now_fields), now_fields)
    old = _index(_get(2018, ["DP05_0001E"]), ["DP05_0001E"])

    rows = []
    for m in metros:
        key = (m["name"].strip().lower(), m["state"])
        c = cur.get(key)
        if not c:
            continue
        try:
            pop = int(float(c["DP05_0001E"]))
            income = int(float(c["DP03_0062E"]))
        except (TypeError, ValueError):
            continue
        o = old.get(key, {}).get("DP05_0001E")
        trend = round((pop / float(o) - 1) * 100, 1) if o and float(o) > 0 else ""
        inds = []
        for f, label in IND_FIELDS.items():
            try:
                inds.append((label, float(c[f])))
            except (TypeError, ValueError):
                continue
        inds.sort(key=lambda x: -x[1])
        row = {"slug": m["slug"], "population": pop, "pop_5yr_pct": trend,
               "income": income}
        for i, (label, share) in enumerate(inds[:5], 1):
            row[f"ind{i}"] = label
            row[f"ind{i}_pct"] = share
        rows.append(row)

    if len(rows) < max(5, len(metros) // 10):
        print(f"[error] only {len(rows)} metros matched Census — name matching "
              "or endpoint likely changed; not writing context file")
        sys.exit(1)
    out = os.path.join(ROOT, "data", "metro_context.csv")
    fields = ["slug", "population", "pop_5yr_pct", "income"] + \
             [f"ind{i}{s}" for i in range(1, 6) for s in ("", "_pct")]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f"[done] context for {len(rows)} metros -> {out}")


if __name__ == "__main__":
    main()
