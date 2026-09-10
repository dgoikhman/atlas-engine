"""Atlas Engine — Franchise Atlas pipeline.

Two stages:
  1) fetch  — pull Franchise Disclosure Document PDFs from Minnesota CARDS
              (free public registry). Wisconsin DFI and California DocQNet
              follow the same pattern later.
  2) extract — Claude Haiku via the Batch API (50% cheaper than realtime)
              turns each FDD into structured JSON: Items 5-7 (costs),
              Item 19 (financial performance), Item 20 (unit counts).

Usage:
  python pipelines/fdd.py fetch --query "coffee" --limit 20
  python pipelines/fdd.py extract data/raw/fdd/*.pdf
  python pipelines/fdd.py poll <batch_id>

Requires: ANTHROPIC_API_KEY env var for extract/poll.

NOTE on fetch: CARDS is a public search portal
(https://www.cards.commerce.state.mn.us/franchise-registrations). The
search endpoint below matches its public URL pattern as of the last check —
if the portal HTML changes, update the CSS selectors marked TODO. You can
always bypass fetch by downloading PDFs manually and running extract on
them; extraction is the valuable half.
"""
import base64, glob, json, os, sys, hashlib
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDD_DIR = os.path.join(ROOT, "data", "raw", "fdd")
OUT_DIR = os.path.join(ROOT, "data", "fdd_extracted")
os.makedirs(FDD_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

CARDS_BASE = "https://www.cards.commerce.state.mn.us"

EXTRACTION_PROMPT = """You are extracting structured data from a US Franchise Disclosure Document (FDD).
Read the document and respond with ONLY valid JSON, no markdown fences, no preamble, exactly this schema:
{
 "brand": "franchise brand name",
 "franchisor": "legal entity name",
 "fdd_year": 2026,
 "item5_initial_fee_low": 0, "item5_initial_fee_high": 0,
 "item7_total_investment_low": 0, "item7_total_investment_high": 0,
 "item7_notable_costs": ["top 3 line items with amounts"],
 "item19_has_fpr": true,
 "item19_summary": "1-2 sentences: what financial performance is disclosed (avg revenue, margins) or 'No FPR provided'",
 "item20_units_total": 0,
 "item20_units_franchised": 0,
 "item20_units_company": 0,
 "item20_3yr_trend": "growing|flat|shrinking",
 "item20_states_top5": ["TX","FL","CA","OH","GA"],
 "royalty_pct": "e.g. 6% of gross sales",
 "ad_fund_pct": "e.g. 2%",
 "term_years": 10,
 "litigation_flag": false,
 "litigation_note": "1 sentence if item 3 discloses material litigation, else empty"
}
Use null for anything genuinely absent. Numbers as integers in dollars."""


def fetch(query: str, limit: int = 20):
    """Search CARDS and download FDD PDFs. Selectors may need a refresh."""
    from html.parser import HTMLParser

    class LinkGrab(HTMLParser):
        def __init__(self):
            super().__init__(); self.pdfs = []
        def handle_starttag(self, tag, attrs):
            if tag == "a":
                href = dict(attrs).get("href", "")
                # TODO: confirm against the live portal — CARDS serves
                # documents through /api/document/ or attachment links.
                if ".pdf" in href.lower() or "/documents/" in href:
                    self.pdfs.append(href if href.startswith("http") else CARDS_BASE + href)

    url = f"{CARDS_BASE}/franchise-registrations?search={requests.utils.quote(query)}"
    print(f"[cards] {url}")
    r = requests.get(url, timeout=60, headers={"User-Agent": "AtlasEngine/0.1 (public records research)"})
    r.raise_for_status()
    p = LinkGrab(); p.feed(r.text)
    if not p.pdfs:
        print("[cards] no document links parsed — portal HTML likely changed; "
              "inspect the page and update LinkGrab, or download PDFs manually "
              f"into {FDD_DIR} and run extract.")
        return
    for u in p.pdfs[:limit]:
        name = hashlib.sha256(u.encode()).hexdigest()[:16] + ".pdf"
        path = os.path.join(FDD_DIR, name)
        if os.path.exists(path):
            continue
        print(f"[cards] downloading {u}")
        d = requests.get(u, timeout=120)
        if d.ok and d.content[:4] == b"%PDF":
            open(path, "wb").write(d.content)
    print(f"[cards] done -> {FDD_DIR}")


def extract(paths):
    """Submit FDD PDFs to the Claude Batch API for structured extraction."""
    import anthropic
    client = anthropic.Anthropic()
    reqs = []
    for path in paths:
        pdf_b64 = base64.standard_b64encode(open(path, "rb").read()).decode()
        reqs.append({
            "custom_id": os.path.basename(path).replace(".pdf", ""),
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1500,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "document",
                         "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                        {"type": "text", "text": EXTRACTION_PROMPT},
                    ],
                }],
            },
        })
    batch = client.messages.batches.create(requests=reqs)
    print(f"[batch] submitted {len(reqs)} docs, batch id: {batch.id}")
    print(f"[batch] poll with: python pipelines/fdd.py poll {batch.id}")


def poll(batch_id: str):
    import anthropic
    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(batch_id)
    print(f"[batch] status: {batch.processing_status}")
    if batch.processing_status != "ended":
        return
    ok = fail = 0
    for result in client.messages.batches.results(batch_id):
        cid = result.custom_id
        if result.result.type == "succeeded":
            text = "".join(b.text for b in result.result.message.content if b.type == "text")
            text = text.replace("```json", "").replace("```", "").strip()
            try:
                data = json.loads(text[text.index("{"): text.rindex("}") + 1])
                # Sanity ranges before anything reaches the site.
                lo, hi = data.get("item7_total_investment_low"), data.get("item7_total_investment_high")
                if lo and hi and (lo > hi or hi > 50_000_000):
                    raise ValueError(f"item7 range implausible: {lo}-{hi}")
                out = os.path.join(OUT_DIR, f"{cid}.json")
                json.dump(data, open(out, "w"), indent=2)
                ok += 1
            except Exception as e:
                print(f"[warn] {cid}: {e} -> flagged for human review")
                json.dump({"raw": text, "error": str(e)},
                          open(os.path.join(OUT_DIR, f"{cid}.REVIEW.json"), "w"))
                fail += 1
        else:
            fail += 1
    print(f"[batch] extracted {ok}, flagged {fail} -> {OUT_DIR}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch":
        q = sys.argv[sys.argv.index("--query") + 1] if "--query" in sys.argv else ""
        n = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 20
        fetch(q, n)
    elif cmd == "extract":
        files = []
        for pat in sys.argv[2:]:
            files.extend(glob.glob(pat))
        if not files:
            sys.exit("no PDFs matched")
        extract(files)
    elif cmd == "poll":
        poll(sys.argv[2])
    else:
        print(__doc__)
