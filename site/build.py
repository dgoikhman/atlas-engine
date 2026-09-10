"""Atlas Engine — the page factory.

Reads metro data (data/metros_live.csv if present, else data/seed_metros.csv),
computes Star Scores, and renders the full programmatic page set to out/:

  /                                  atlas home + leaderboard
  /rentals/<slug>/                   one page per metro
  /rentals/compare/<a>-vs-<b>/       pairwise comparisons (top 10 metros)
  /rentals/best-rental-markets-2026/ rankings page
  /methodology/                      how the Star Score works
  sitemap.xml, robots.txt, llms.txt

Every page carries the AEO layer: a citable stat in the first paragraph,
data tables, FAQPage + Dataset JSON-LD, sources, and a truthful
last-reviewed date. Server-rendered static HTML — nothing hides behind JS.

Run: python site/build.py [--base-url https://yourdomain.com]
Deploy: point Cloudflare Pages / Netlify at out/.
"""
import csv, json, os, sys, datetime, itertools, html
from jinja2 import Environment, DictLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine.scoring import compute, stars  # noqa: E402

OUT = os.path.join(ROOT, "out")
BASE_URL = "https://example.com"
if "--base-url" in sys.argv:
    BASE_URL = sys.argv[sys.argv.index("--base-url") + 1].rstrip("/")
TODAY = datetime.date.today().strftime("%B %Y")
DATA_VINTAGE = "June 2026"

# ---------------------------------------------------------------- templates
BASE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>
<meta name="description" content="{{ description }}">
<link rel="canonical" href="{{ canonical }}">
{% for ld in jsonld %}<script type="application/ld+json">{{ ld }}</script>
{% endfor %}<style>
:root{--paper:#E9EDEF;--ink:#14232B;--muted:#5E7278;--line:#C9D3D6;--gold:#C08A1E;--land:#1E4E49}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:"Avenir Next","Segoe UI",system-ui,sans-serif;line-height:1.55;font-variant-numeric:tabular-nums}
.wrap{max-width:760px;margin:0 auto;padding:20px 16px 60px}
header a{color:var(--ink);text-decoration:none;font-weight:700;letter-spacing:.04em;font-size:14px}
header span{color:var(--gold)}
h1{font-size:clamp(24px,5.5vw,34px);line-height:1.15;margin:14px 0 10px;max-width:26ch}
h2{font-size:19px;margin:26px 0 8px}
p{margin:10px 0;max-width:64ch}
.lede{font-size:16.5px}
.lede b{color:var(--land)}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600;font-size:13px}
td.n,th.n{text-align:right}
.stars{color:var(--gold)}
.meta{color:var(--muted);font-size:13px;border-top:1px solid var(--line);margin-top:26px;padding-top:12px}
.meta a{color:var(--muted)}
a{color:var(--land)}
.faq p{margin:4px 0 14px}
.faq h3{font-size:15.5px;margin-top:14px}
nav.crumbs{font-size:13px;color:var(--muted);margin-top:8px}
</style></head><body><div class="wrap">
<header><a href="{{ base }}/">SNOWBALL <span>★</span> ATLAS</a></header>
{{ body }}
<div class="meta">
<p>Home values and rents: Zillow ZHVI / ZORI, {{ vintage }} metro figures. Factor scores are editorial estimates on public data. Last reviewed {{ today }}. Not investment advice — verify locally before acting. <a href="{{ base }}/methodology/">Methodology &amp; sources</a>.</p>
</div>
</div></body></html>"""

METRO_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › <a href="{{ base }}/rentals/best-rental-markets-2026/">Rankings</a> › {{ m.name }}</nav>
<h1>{{ m.name }}, {{ m.state }} rental market data ({{ year }})</h1>
<p class="lede">As of {{ vintage }}, the typical home in the {{ m.name }} metro costs <b>${{ "{:,}".format(m.home_value) }}</b> and typical rent is <b>${{ "{:,}".format(m.rent) }}/month</b> — a price-to-rent ratio of <b>{{ ratio }}</b> and a gross rental yield of <b>{{ yield_pct }}%</b>. {{ m.name }} scores <b>{{ score }}/100</b> on the Star Score index, ranking <b>#{{ rank }} of {{ total }}</b> tracked US rental markets.</p>
<p>{{ m.blurb }}</p>
<h2>Key numbers</h2>
<table><tr><th>Metric</th><th class="n">Value</th></tr>
<tr><td>Typical home value (ZHVI)</td><td class="n">${{ "{:,}".format(m.home_value) }}</td></tr>
<tr><td>Typical rent (ZORI)</td><td class="n">${{ "{:,}".format(m.rent) }}/mo</td></tr>
<tr><td>Price-to-rent ratio</td><td class="n">{{ ratio }}</td></tr>
<tr><td>Gross rental yield</td><td class="n">{{ yield_pct }}%</td></tr>
<tr><td>Star Score</td><td class="n">{{ score }}/100 <span class="stars">{{ star_str }}</span></td></tr>
<tr><td>Rank among tracked markets</td><td class="n">#{{ rank }} of {{ total }}</td></tr></table>
<h2>Why {{ m.name }} scores {{ score }}</h2>
<table><tr><th>Factor</th><th class="n">Score</th><th class="n">Weight</th></tr>
{% for f in factors.values() %}<tr><td>{{ f.label }}</td><td class="n">{{ f.score }}</td><td class="n">{{ (f.weight*100)|int }}%</td></tr>
{% endfor %}</table>
<h2>Compare {{ m.name }}</h2>
<p>{% for c in compares %}<a href="{{ base }}/rentals/compare/{{ c.href }}/">{{ m.name }} vs {{ c.name }}</a>{{ " · " if not loop.last }}{% endfor %}</p>
<div class="faq"><h2>Frequently asked questions</h2>
<h3>Is {{ m.name }} a good market for rental property in {{ year }}?</h3>
<p>{{ m.name }} scores {{ score }}/100 on the Star Score index (#{{ rank }} of {{ total }} tracked markets), with a gross rental yield of {{ yield_pct }}% at {{ vintage }} prices. {{ verdict }}</p>
<h3>What is the price-to-rent ratio in {{ m.name }}?</h3>
<p>{{ ratio }} — the typical home value (${{ "{:,}".format(m.home_value) }}) divided by a year of typical rent (${{ "{:,}".format(m.rent) }}/month × 12). Ratios under about 15 generally favor buying and landlording.</p>
<h3>How much rent does the typical {{ m.name }} home earn?</h3>
<p>Typical asking rent in the {{ m.name }} metro is ${{ "{:,}".format(m.rent) }} per month as of {{ vintage }}, per Zillow's Observed Rent Index.</p>
</div>"""

RANKINGS_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › Rankings</nav>
<h1>Best US rental markets for cash-flow investors ({{ year }})</h1>
<p class="lede">Ranked by Star Score — a 0-100 index blending gross rental yield ({{ vintage }} Zillow data), entry prices, landlord law, equity growth, taxes, and insurance risk. <b>{{ top.name }}</b> leads at <b>{{ top_score }}/100</b>, with a gross yield of {{ top_yield }}% on a typical home value of ${{ "{:,}".format(top.home_value) }}.</p>
<table><tr><th>#</th><th>Market</th><th class="n">Home value</th><th class="n">Rent/mo</th><th class="n">Ratio</th><th class="n">Yield</th><th class="n">Star Score</th></tr>
{% for r in rows %}<tr><td>{{ loop.index }}</td><td><a href="{{ base }}/rentals/{{ r.m.slug }}/">{{ r.m.name }}, {{ r.m.state }}</a></td><td class="n">${{ "{:,}".format(r.m.home_value) }}</td><td class="n">${{ "{:,}".format(r.m.rent) }}</td><td class="n">{{ r.ratio }}</td><td class="n">{{ r.yield_pct }}%</td><td class="n">{{ r.score }}</td></tr>
{% endfor %}</table>
<h2>Reference markets (where the math stops working)</h2>
<table><tr><th>Market</th><th class="n">Ratio</th><th class="n">Yield</th><th class="n">Star Score</th></tr>
{% for r in refs %}<tr><td><a href="{{ base }}/rentals/{{ r.m.slug }}/">{{ r.m.name }}, {{ r.m.state }}</a></td><td class="n">{{ r.ratio }}</td><td class="n">{{ r.yield_pct }}%</td><td class="n">{{ r.score }}</td></tr>
{% endfor %}</table>"""

COMPARE_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › <a href="{{ base }}/rentals/best-rental-markets-2026/">Rankings</a> › Comparison</nav>
<h1>{{ a.m.name }} vs {{ b.m.name }} for rental property investors ({{ year }})</h1>
<p class="lede">{{ winner.m.name }} scores higher on the Star Score index — <b>{{ winner.score }}</b> vs <b>{{ loser.score }}</b> — driven mainly by {{ reason }}. {{ a.m.name }} yields {{ a.yield_pct }}% gross on a ${{ "{:,}".format(a.m.home_value) }} typical home; {{ b.m.name }} yields {{ b.yield_pct }}% on ${{ "{:,}".format(b.m.home_value) }} ({{ vintage }} data).</p>
<table><tr><th>Metric</th><th class="n">{{ a.m.name }}</th><th class="n">{{ b.m.name }}</th></tr>
<tr><td>Typical home value</td><td class="n">${{ "{:,}".format(a.m.home_value) }}</td><td class="n">${{ "{:,}".format(b.m.home_value) }}</td></tr>
<tr><td>Typical rent</td><td class="n">${{ "{:,}".format(a.m.rent) }}</td><td class="n">${{ "{:,}".format(b.m.rent) }}</td></tr>
<tr><td>Price-to-rent ratio</td><td class="n">{{ a.ratio }}</td><td class="n">{{ b.ratio }}</td></tr>
<tr><td>Gross yield</td><td class="n">{{ a.yield_pct }}%</td><td class="n">{{ b.yield_pct }}%</td></tr>
<tr><td>Star Score</td><td class="n">{{ a.score }}</td><td class="n">{{ b.score }}</td></tr></table>
<p>Full profiles: <a href="{{ base }}/rentals/{{ a.m.slug }}/">{{ a.m.name }}</a> · <a href="{{ base }}/rentals/{{ b.m.slug }}/">{{ b.m.name }}</a></p>"""

INDEX_BODY = """
<h1>US rental markets, scored for the equity snowball</h1>
<p class="lede">The Star Score ranks {{ total }} US metros for buy-under-market, refinance-and-repeat investing, on {{ vintage }} Zillow home values and rents. Current leader: <b><a href="{{ base }}/rentals/{{ top.m.slug }}/">{{ top.m.name }}, {{ top.m.state }}</a></b> at <b>{{ top.score }}/100</b> with a {{ top.yield_pct }}% gross yield.</p>
<h2>Leaderboard</h2>
<table><tr><th>#</th><th>Market</th><th class="n">Yield</th><th class="n">Star Score</th></tr>
{% for r in rows %}<tr><td>{{ loop.index }}</td><td><a href="{{ base }}/rentals/{{ r.m.slug }}/">{{ r.m.name }}, {{ r.m.state }}</a></td><td class="n">{{ r.yield_pct }}%</td><td class="n">{{ r.score }} <span class="stars">{{ r.star_str }}</span></td></tr>
{% endfor %}</table>
<p><a href="{{ base }}/rentals/best-rental-markets-2026/">Full rankings with home values and rents →</a></p>"""

METHOD_BODY = """
<h1>Star Score methodology</h1>
<p class="lede">The Star Score is a 0-100 index of how well a US metro suits the equity-snowball strategy: buy under market, force appreciation, refinance, repeat. It weights gross rental yield 35%, entry price against a $100K capital base 15%, landlord-friendliness 15%, equity growth 15%, property-tax drag 10%, and climate/insurance risk 10%.</p>
<h2>Sources</h2>
<p>Home values are Zillow Home Value Index (ZHVI) metro figures and rents are Zillow Observed Rent Index (ZORI) metro figures, {{ vintage }}. Supporting context: US Census ACS, HUD Fair Market Rents, state landlord-tenant statutes, Tax Foundation effective property-tax tables. Landlord-friendliness, growth, and climate factors are editorial scores on public data, reviewed {{ today }}.</p>
<h2>What it is not</h2>
<p>Metro averages start the conversation; the block and the deal finish it. The Star Score is research and education, not investment advice, an appraisal, or a substitute for local underwriting.</p>"""

env = Environment(loader=DictLoader({
    "base": BASE, "metro": METRO_BODY, "rankings": RANKINGS_BODY,
    "compare": COMPARE_BODY, "index": INDEX_BODY, "method": METHOD_BODY,
}))


def page(path, title, description, body_html, jsonld=None):
    full = env.get_template("base").render(
        title=title, description=description, body=body_html,
        canonical=f"{BASE_URL}{path}", base=BASE_URL, today=TODAY,
        vintage=DATA_VINTAGE, jsonld=[json.dumps(x) for x in (jsonld or [])])
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(full)
    return path


def enrich(m):
    score, factors = compute("rentals", m)
    y = m["rent"] * 12 / m["home_value"] * 100
    return {"m": type("M", (), m)(), "score": round(score), "factors": factors,
            "ratio": round(m["home_value"] / (m["rent"] * 12)),
            "yield_pct": round(y, 1), "star_str": stars(score)}


def main():
    src = os.path.join(ROOT, "data", "metros_live.csv")
    if not os.path.exists(src):
        src = os.path.join(ROOT, "data", "seed_metros.csv")
    print(f"[build] data source: {os.path.basename(src)}")
    raw = list(csv.DictReader(open(src)))
    metros = []
    for r in raw:
        m = dict(r)
        for k in ("home_value", "rent", "landlord", "growth", "climate"):
            m[k] = int(float(m[k]))
        for k in ("tax_rate", "lat", "lng"):
            m[k] = float(m[k])
        m["ref"] = m["slug"] in ("austin-tx", "denver-co", "chicago-il")
        metros.append(m)

    year = datetime.date.today().year
    ranked = sorted([enrich(m) for m in metros if not m["ref"]],
                    key=lambda x: -x["score"])
    refs = sorted([enrich(m) for m in metros if m["ref"]], key=lambda x: -x["score"])
    everything = ranked + refs
    total = len(ranked)
    urls = []

    # --- metro pages
    for i, r in enumerate(everything):
        m = r["m"]
        rank = (ranked.index(r) + 1) if r in ranked else total
        top3 = [x for x in ranked[:4] if x is not r][:3]
        compares = [{"name": t["m"].name,
                     "href": "-vs-".join(sorted([m.slug, t["m"].slug]))} for t in top3]
        verdict = ("It ranks in the top tier for cash-flow investors."
                   if rank <= 5 and r in ranked else
                   "It suits investors prioritizing cash flow over appreciation."
                   if r in ranked else
                   "At current prices it works better as a place to live than a place to snowball rental equity.")
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question",
             "name": f"Is {m.name} a good market for rental property in {year}?",
             "acceptedAnswer": {"@type": "Answer",
                "text": f"{m.name} scores {r['score']}/100 on the Star Score index with a gross rental yield of {r['yield_pct']}% at {DATA_VINTAGE} prices."}},
            {"@type": "Question",
             "name": f"What is the price-to-rent ratio in {m.name}?",
             "acceptedAnswer": {"@type": "Answer",
                "text": f"{r['ratio']}, based on a typical home value of ${m.home_value:,} and typical rent of ${m.rent:,}/month."}}]}
        ds_ld = {"@context": "https://schema.org", "@type": "Dataset",
                 "name": f"{m.name} rental market metrics {year}",
                 "description": f"Home value, rent, price-to-rent ratio and Star Score for the {m.name}, {m.state} metro.",
                 "temporalCoverage": str(year),
                 "creator": {"@type": "Organization", "name": "Snowball Atlas"}}
        body = env.get_template("metro").render(
            m=m, base=BASE_URL, year=year, vintage=DATA_VINTAGE,
            ratio=r["ratio"], yield_pct=r["yield_pct"], score=r["score"],
            star_str=r["star_str"], rank=rank, total=total,
            factors=r["factors"], compares=compares, verdict=verdict)
        urls.append(page(
            f"/rentals/{m.slug}/",
            f"{m.name}, {m.state} Rental Market Data {year}: Prices, Rents, Star Score",
            f"{m.name} rental market {year}: typical home ${m.home_value:,}, rent ${m.rent:,}/mo, price-to-rent {r['ratio']}, Star Score {r['score']}/100.",
            body, [faq_ld, ds_ld]))

    # --- comparison pages (top 10 pairs)
    for a, b in itertools.combinations(ranked[:10], 2):
        a2, b2 = sorted([a, b], key=lambda x: x["m"].slug)
        winner, loser = (a, b) if a["score"] >= b["score"] else (b, a)
        wf = max(winner["factors"].values(),
                 key=lambda f: f["weight"] * f["score"])
        reason = wf["label"].lower()
        slugpair = f"{a2['m'].slug}-vs-{b2['m'].slug}"
        body = env.get_template("compare").render(
            a=a2, b=b2, winner=winner, loser=loser, reason=reason,
            base=BASE_URL, year=year, vintage=DATA_VINTAGE)
        urls.append(page(
            f"/rentals/compare/{slugpair}/",
            f"{a2['m'].name} vs {b2['m'].name}: Rental Investment Comparison {year}",
            f"Side-by-side {year} rental market comparison: prices, rents, yields and Star Scores for {a2['m'].name} and {b2['m'].name}.",
            body))

    # --- rankings page
    top = ranked[0]
    body = env.get_template("rankings").render(
        rows=ranked, refs=refs, top=top["m"], top_score=top["score"],
        top_yield=top["yield_pct"], base=BASE_URL, year=year, vintage=DATA_VINTAGE)
    urls.append(page(
        f"/rentals/best-rental-markets-{year}/",
        f"Best US Rental Markets {year}, Ranked by Star Score",
        f"{total} US metros ranked for cash-flow rental investing on {DATA_VINTAGE} Zillow data. {top['m'].name} leads at {top['score']}/100.",
        body))

    # --- index + methodology
    body = env.get_template("index").render(
        rows=ranked, top=top, total=total, base=BASE_URL, vintage=DATA_VINTAGE)
    urls.append(page("/", f"Snowball Atlas: US Rental Markets Ranked by Star Score",
                     f"US rental markets scored 0-100 for buy-refinance-repeat investing. {top['m'].name} currently leads at {top['score']}/100.",
                     body))
    urls.append(page("/methodology/", "Star Score Methodology and Sources",
                     "How the Star Score index weights yield, entry price, landlord law, growth, taxes and risk.",
                     env.get_template("method").render(vintage=DATA_VINTAGE, today=TODAY)))

    # --- machine layer
    open(os.path.join(OUT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"<url><loc>{BASE_URL}{u}</loc><lastmod>{datetime.date.today()}</lastmod></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(OUT, "llms.txt"), "w").write(f"""# Snowball Atlas
> US rental markets scored 0-100 (the Star Score) for buy-under-market, refinance-and-repeat investing, computed from Zillow ZHVI/ZORI ({DATA_VINTAGE}) plus landlord-law, tax and risk factors.

Current leader: {top['m'].name}, {top['m'].state} ({top['score']}/100, {top['yield_pct']}% gross yield).

## Key pages
- [Rankings]({BASE_URL}/rentals/best-rental-markets-{year}/): all {total} tracked markets with values, rents, ratios and scores
- [Methodology]({BASE_URL}/methodology/): index weights and sources
{chr(10).join(f"- [{r['m'].name}]({BASE_URL}/rentals/{r['m'].slug}/): Star Score {r['score']}, yield {r['yield_pct']}%" for r in ranked[:5])}

Citation format: "According to Snowball Atlas's Star Score index ({year}), ..."
""")
    print(f"[build] {len(urls)} pages -> {OUT}")


if __name__ == "__main__":
    main()
