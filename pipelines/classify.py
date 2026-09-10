"""Main Street Atlas — industry classification + Roll-up Radar.

Stage 1 (classify): entity names -> industry labels via Claude Haiku Batch
API, strict JSON, confidence-scored. ~$1 per 10K names.
Stage 2 (radar): aggregate classified entities into the Roll-up Radar —
per (city x vertical): count of aged independents, i.e. fragmentation.
Radar aggregates are safe to publish (counts, no names); the classified
entity list itself stays in data/pro/ (gitignored).

Usage:
  python pipelines/classify.py submit          # batch the unclassified
  python pipelines/classify.py poll <batch_id>
  python pipelines/classify.py radar           # build rollup_radar.csv
Requires ANTHROPIC_API_KEY for submit/poll.
"""
import csv, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENT = os.path.join(ROOT, "data", "pro", "mainstreet_entities.csv")
CLS = os.path.join(ROOT, "data", "pro", "entities_classified.csv")
RADAR = os.path.join(ROOT, "data", "rollup_radar.csv")   # aggregates: publishable

VERTICALS = ["hvac", "plumbing", "electrical", "roofing", "landscaping",
             "cleaning-laundry", "auto-repair", "dental", "veterinary",
             "accounting", "law", "insurance-agency", "manufacturing",
             "distribution-wholesale", "construction", "trucking-logistics",
             "restaurant", "retail", "property-services", "salon-fitness",
             "childcare", "funeral", "storage", "other", "holding-nonoperating"]

PROMPT = ("For each numbered business entity name, classify its likely industry. "
          "Respond ONLY with compact JSON: {\"r\":[{\"i\":1,\"v\":\"hvac\",\"c\":0.9}]} "
          "where v is exactly one of: " + ", ".join(VERTICALS) +
          ". c is confidence 0-1. Use holding-nonoperating for LLCs that look like "
          "asset/property holders, family trusts, or shells; use other when unclear. "
          "Names:\n")


def auto():
    """submit -> wait -> process -> radar, in one run (for CI)."""
    import anthropic, time
    bid = submit()
    if not bid:
        return radar()
    client = anthropic.Anthropic()
    for _ in range(90):                      # up to ~45 min
        b = client.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            poll(bid); return radar()
        print(f"[classify] {b.processing_status}...", flush=True)
        time.sleep(30)
    print("[classify] batch still running — poll later with:", bid)


def submit():
    import anthropic
    client = anthropic.Anthropic()
    done = set()
    if os.path.exists(CLS):
        done = {r["entity_id"] for r in csv.DictReader(open(CLS))}
    ents = [r for r in csv.DictReader(open(ENT)) if r["entity_id"] not in done]
    cap = int(os.environ.get("CLASSIFY_CAP", "20000"))
    ents = ents[:cap]
    if not ents:
        print("[classify] nothing new"); return None
    reqs, chunk = [], 40
    for i in range(0, len(ents), chunk):
        grp = ents[i:i + chunk]
        names = "\n".join(f"{j+1}. {e['name']}" for j, e in enumerate(grp))
        reqs.append({"custom_id": f"c{i}",
                     "params": {"model": "claude-haiku-4-5-20251001", "max_tokens": 1400,
                                "messages": [{"role": "user", "content": PROMPT + names}]}})
    batch = client.messages.batches.create(requests=reqs)
    json.dump({"batch": batch.id, "offset_map": {f"c{i}": [e["entity_id"] for e in ents[i:i+chunk]]
               for i in range(0, len(ents), chunk)}},
              open(os.path.join(ROOT, "data", "pro", "classify_state.json"), "w"))
    print(f"[classify] submitted {len(ents)} names in {len(reqs)} requests, batch {batch.id}")
    return batch.id


def poll(batch_id):
    import anthropic
    client = anthropic.Anthropic()
    st = json.load(open(os.path.join(ROOT, "data", "pro", "classify_state.json")))
    batch = client.messages.batches.retrieve(batch_id)
    print(f"[classify] {batch.processing_status}")
    if batch.processing_status != "ended":
        return
    ents = {r["entity_id"]: r for r in csv.DictReader(open(ENT))}
    exists = os.path.exists(CLS)
    with open(CLS, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["entity_id", "name", "city", "zip",
                                          "age_years", "vertical", "confidence"])
        if not exists:
            w.writeheader()
        ok = 0
        for res in client.messages.batches.results(batch_id):
            ids = st["offset_map"].get(res.custom_id, [])
            if res.result.type != "succeeded":
                continue
            text = "".join(b.text for b in res.result.message.content if b.type == "text")
            try:
                data = json.loads(text[text.index("{"):text.rindex("}") + 1])
                for item in data.get("r", []):
                    idx = item["i"] - 1
                    if idx >= len(ids):
                        continue
                    e = ents.get(ids[idx])
                    if not e or item.get("v") not in VERTICALS:
                        continue
                    w.writerow({"entity_id": e["entity_id"], "name": e["name"],
                                "city": e["city"], "zip": e["zip"],
                                "age_years": e["age_years"],
                                "vertical": item["v"], "confidence": item.get("c", 0)})
                    ok += 1
            except Exception:
                continue
    print(f"[classify] wrote {ok} classifications -> {CLS}")


def radar():
    agg = defaultdict(int)
    for r in csv.DictReader(open(CLS)):
        if float(r["confidence"] or 0) < 0.6:
            continue
        if r["vertical"] in ("other", "holding-nonoperating"):
            continue
        agg[(r["city"], r["vertical"])] += 1
    rows = [{"city": c, "vertical": v, "aged_independents": n}
            for (c, v), n in sorted(agg.items(), key=lambda x: -x[1])]
    with open(RADAR, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["city", "vertical", "aged_independents"])
        w.writeheader(); w.writerows(rows)
    print(f"[radar] {len(rows)} city x vertical cells -> {RADAR} (aggregate counts only: publishable)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "submit": submit()
    elif cmd == "auto": auto()
    elif cmd == "poll": poll(sys.argv[2])
    elif cmd == "radar": radar()
    else: print(__doc__)
