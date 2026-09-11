"""BRRRR Markets — Star Opportunities (licensed listings via RentCast).

Pulls active sale listings for the top-scored metros, flags under-market
signals (price cuts, long days-on-market, below-batch $/sqft), scores each
as a Star Opportunity, and writes data/star_opportunities.json for the site
builder. Runs in CI at build time; output is regenerated fresh each run and
is NOT committed (licensed data is displayed, not redistributed).

Freshness gradient: the top LISTINGS_DAILY metros scan every run; all
remaining metros rotate through LISTINGS_ROTATION_DAYS buckets (each market
refreshed once per cycle). Prior results carry forward with their as_of
date. Defaults (15 daily / 14-day rotation) ≈ 1,000 calls/mo — fits
RentCast's entry paid tier. Weekly rotation ≈ 1,900/mo; full national
daily ≈ 9-12K/mo (their top tier). Set via repo variables.

Env: RENTCAST_API_KEY (required; exits quietly without it)
     LISTINGS_DAILY (default 15), LISTINGS_ROTATION_DAYS (default 14)
Test: LISTINGS_LOCAL=data/test_fixtures python pipelines/listings.py
"""
import csv, json, os, statistics, sys, time
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.rentcast.io/v1/listings/sale"
N_DAILY = int(os.environ.get("LISTINGS_DAILY") or os.environ.get("LISTINGS_METROS") or "15")
ROT_DAYS = int(os.environ.get("LISTINGS_ROTATION_DAYS") or "14")
OUT = os.path.join(ROOT, "data", "star_opportunities.json")


def fetch(city, state, key):
    local = os.environ.get("LISTINGS_LOCAL")
    if local:
        p = os.path.join(local, f"rc_{city.lower().replace(' ', '')}.json")
        return json.load(open(p)) if os.path.exists(p) else []
    out = []
    for offset in (0, 500):                  # up to 1,000 listings per metro
        r = requests.get(API, params={"city": city, "state": state,
                                      "status": "Active", "limit": 500,
                                      "offset": offset},
                         headers={"X-Api-Key": key}, timeout=60)
        if r.status_code == 401:
            sys.exit("[listings] API key rejected by RentCast")
        if r.status_code == 429:
            print(f"[listings] {city}: rate/quota limit hit — stopping this run")
            return out
        if not r.ok:
            print(f"[listings] {city}: HTTP {r.status_code} — skipping")
            return out
        batch = r.json()
        out.extend(batch)
        if len(batch) < 500:
            break
    return out


def score_metro(listings, metro_rent, metro_value):
    """Flag and score under-market candidates within one metro's batch."""
    cands = []
    psf = [l["price"] / l["squareFootage"] for l in listings
           if l.get("price") and l.get("squareFootage") and l["squareFootage"] > 300]
    med_psf = statistics.median(psf) if len(psf) >= 10 else None
    for l in listings:
        price, sqft = l.get("price"), l.get("squareFootage")
        if not price or price < 40000 or price > metro_value * 1.2:
            continue
        dom = l.get("daysOnMarket") or 0
        cut = 0.0
        hist = l.get("history") or {}
        events = sorted(hist.items())
        prices = [e[1].get("price") for e in events if e[1].get("price")]
        if len(prices) >= 2 and max(prices) > 0:
            cut = max(0.0, (max(prices) - price) / max(prices) * 100)
        below = 0.0
        if med_psf and sqft and sqft > 300:
            below = max(0.0, (1 - (price / sqft) / med_psf) * 100)
        if cut < 4 and dom < 45 and below < 15:
            continue                      # no under-market signal
        under = round(min(30.0, max(cut, below * 0.8)), 1)
        # modeled rent: metro typical rent scaled by size vs a 1,400 sqft ref
        est_rent = round(metro_rent * min(1.5, max(0.6, (sqft or 1400) / 1400)) / 10) * 10
        rent_pct = est_rent / price * 100
        s = max(5, min(100, under * 3.2 + (rent_pct - 0.75) * 80))
        cands.append({
            "addr": l.get("formattedAddress", "Listing"),
            "price": price, "beds": l.get("bedrooms"), "baths": l.get("bathrooms"),
            "sqft": sqft, "dom": dom, "cut_pct": round(cut, 1),
            "under_pct": under, "est_rent": est_rent,
            "yield_pct": round(est_rent * 12 / price * 100, 1),
            "score": round(s),
        })
    cands.sort(key=lambda c: -c["score"])
    return cands[:5]


def main():
    key = os.environ.get("RENTCAST_API_KEY", "")
    if not key and not os.environ.get("LISTINGS_LOCAL"):
        print("[listings] RENTCAST_API_KEY unset — Star Opportunities dormant")
        return
    src = os.path.join(ROOT, "data", "metros_live.csv")
    if not os.path.exists(src):
        src = os.path.join(ROOT, "data", "seed_metros.csv")
    sys.path.insert(0, ROOT)
    from engine.scoring import compute
    metros = []
    for m in csv.DictReader(open(src)):
        d = {k: (float(m[k]) if k in ("tax_rate",) else int(float(m[k])))
             for k in ("home_value", "rent", "landlord", "tax_rate", "growth", "climate")}
        sc, _ = compute("rentals", d)
        metros.append((sc, m["slug"], m["name"], m["state"], d))
    metros.sort(reverse=True)
    import datetime as _dt
    day = _dt.date.today().toordinal()
    rest = metros[N_DAILY:]
    todays_slice = [m for i, m in enumerate(rest) if i % ROT_DAYS == day % ROT_DAYS]
    scan_list = metros[:N_DAILY] + todays_slice
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    total = 0
    print(f"[listings] scanning {len(scan_list)} metros "
          f"({N_DAILY} daily + {len(todays_slice)} rotation of {len(rest)}, "
          f"cycle {ROT_DAYS}d)")
    for sc, slug, name, state, d in scan_list:
        listings = fetch(name, state, key)
        picks = score_metro(listings, d["rent"], d["home_value"])
        if picks:
            out[slug] = {"as_of": time.strftime("%Y-%m-%d"), "items": picks}
            total += len(picks)
        elif slug in out and listings:
            out.pop(slug)                    # scanned fresh, nothing qualifies now
        print(f"[listings] {name}: {len(listings)} active, {len(picks)} flagged")
        time.sleep(0.4)
    json.dump(out, open(OUT, "w"))
    print(f"[listings] flagged {total} Star Opportunities across {len(out)} metros -> {OUT}")


if __name__ == "__main__":
    main()
