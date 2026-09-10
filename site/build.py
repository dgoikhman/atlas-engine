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
STRIPE_ANNUAL = os.environ.get("STRIPE_LINK_ANNUAL", "")
STRIPE_PASS = os.environ.get("STRIPE_LINK_PASS", "")
FORM_ENDPOINT = os.environ.get("FORM_ENDPOINT", "")
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
.explain{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:12px 14px;margin:14px 0;font-size:14px}
.explain b{color:var(--land)}
.map-wrap{background:var(--panel);border:1px solid var(--line);border-radius:6px;margin:14px 0;overflow:hidden}
.map-wrap svg{display:block;width:100%;height:auto}
.quick{font-size:14.5px;margin:10px 0}
.field{margin:8px 0}.field label{display:block;font-size:12.5px;color:var(--muted)}
.field input,.field select{width:100%;font:inherit;font-size:15px;padding:9px;border:1px solid var(--line);border-radius:4px;background:#fff;color:var(--ink)}
.cgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.verdict{margin-top:12px;padding:12px;border-radius:4px;background:#fff;border:1px solid var(--line);font-size:14px}
.verdict b{color:#2E6E4E}.verdict.bad b{color:#B5563F}
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
<div class="explain"><b>New to this?</b> The <b>price-to-rent ratio</b> is the home price divided by a year of rent — lower means rents are big relative to prices, which favors landlords. <b>Gross yield</b> is a year of rent as a % of the price, before expenses. <b>BRRRR</b> = Buy, Rehab, Rent, Refinance, Repeat: buy below market, fix it, rent it, then refinance to pull your cash back out and buy the next one. Full walkthrough in the <a href="{{ base }}/rentals/brrrr-guide/">beginner's guide</a>.</div>
<h2>Key numbers</h2>
<table><tr><th>Metric</th><th class="n">Value</th></tr>
<tr><td>Typical home value (ZHVI)</td><td class="n">${{ "{:,}".format(m.home_value) }}</td></tr>
<tr><td>Typical rent (ZORI)</td><td class="n">${{ "{:,}".format(m.rent) }}/mo</td></tr>
<tr><td>Price-to-rent ratio</td><td class="n">{{ ratio }}</td></tr>
<tr><td>Gross rental yield</td><td class="n">{{ yield_pct }}%</td></tr>
<tr><td>Star Score</td><td class="n">{{ score }}/100 <span class="stars">{{ star_str }}</span></td></tr>
<tr><td>Rank among tracked markets</td><td class="n">#{{ rank }} of {{ total }}</td></tr></table>
<h2>Why {{ m.name }} scores {{ score }}</h2>
{% if unlocked %}<table><tr><th>Factor</th><th class="n">Score</th><th class="n">Weight</th></tr>
{% for f in factors.values() %}<tr><td>{{ f.label }}</td><td class="n">{{ f.score }}</td><td class="n">{{ (f.weight*100)|int }}%</td></tr>
{% endfor %}</table>{% else %}<div class="explain"><b>Factor breakdown is a Pro layer for this market.</b> The top 15 markets show it free — see the <a href="{{ base }}/rentals/best-rental-markets-2026/">rankings</a> — or <a href="{{ base }}/pro/">unlock all {{ total }} markets</a>. Not sure where to start? <a href="{{ base }}/start/">Find your market in 5 taps</a>.</div>{% endif %}
<p class="quick">More context: <a href="{{ base }}/rentals/{{ m.slug }}/living/">Living in {{ m.name }} — economy, industries &amp; affordability</a></p>
<h2>Compare {{ m.name }}</h2>
<p>{% for c in compares %}<a href="{{ base }}/rentals/compare/{{ c.href }}/">{{ m.name }} vs {{ c.name }}</a>{{ " · " if not loop.last }}{% endfor %}</p>
<h2>What would a rehab cost here?</h2>
<p>National rule-of-thumb renovation costs (2026, per square foot) applied to a typical ~1,400 sq ft single-family in this market — every house differs, so treat these as planning ranges, not bids:</p>
<table><tr><th>Scope</th><th class="n">$/sq ft</th><th class="n">Typical house</th></tr>
<tr><td>Paint &amp; refresh (cosmetic light)</td><td class="n">$15–25</td><td class="n">$21K–35K</td></tr>
<tr><td>Cosmetic full (floors, kitchen refresh, baths)</td><td class="n">$25–45</td><td class="n">$35K–63K</td></tr>
<tr><td>Full renovation (systems + finishes)</td><td class="n">$45–75</td><td class="n">$63K–105K</td></tr>
<tr><td>Gut / structural</td><td class="n">$75–120</td><td class="n">$105K–168K</td></tr></table>
<p class="quick">Run your own numbers for {{ m.name }} in the <a href="{{ base }}/rentals/brrrr-calculator/">BRRRR &amp; rehab calculator</a>.</p>
<div class="faq"><h2>Frequently asked questions</h2>
<h3>Is {{ m.name }} a good market for rental property in {{ year }}?</h3>
<p>{{ m.name }} scores {{ score }}/100 on the Star Score index (#{{ rank }} of {{ total }} tracked markets), with a gross rental yield of {{ yield_pct }}% at {{ vintage }} prices. {{ verdict }}</p>
<h3>What is the price-to-rent ratio in {{ m.name }}?</h3>
<p>{{ ratio }} — the typical home value (${{ "{:,}".format(m.home_value) }}) divided by a year of typical rent (${{ "{:,}".format(m.rent) }}/month × 12). Ratios under about 15 generally favor buying and landlording.</p>
<h3>Is {{ m.name }} a good BRRRR market in {{ year }}?</h3>
<p>{{ brrrr_answer }}</p>
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
<div class="map-wrap">{{ map_svg }}</div>
<p class="quick">Bigger star = better snowball math. <b><a href="{{ base }}/start/">Find your market in 5 taps →</a></b></p>
<p class="quick">New here? The <a href="{{ base }}/rentals/brrrr-guide/">2-minute BRRRR guide</a> · <a href="{{ base }}/rentals/brrrr-calculator/">deal calculator</a> · <a href="{{ base }}/pro/">Pro</a></p>
<h2>Leaderboard</h2>
<table><tr><th>#</th><th>Market</th><th class="n">Yield</th><th class="n">Star Score</th></tr>
{% for r in rows[:25] %}<tr><td>{{ loop.index }}</td><td><a href="{{ base }}/rentals/{{ r.m.slug }}/">{{ r.m.name }}, {{ r.m.state }}</a></td><td class="n">{{ r.yield_pct }}%</td><td class="n">{{ r.score }} <span class="stars">{{ r.star_str }}</span></td></tr>
{% endfor %}</table>
<p><a href="{{ base }}/rentals/best-rental-markets-2026/">All {{ total }} ranked markets with home values and rents →</a></p>"""

METHOD_BODY = """
<h1>Star Score methodology</h1>
<p class="lede">The Star Score is a 0-100 index of how well a US metro suits the equity-snowball strategy: buy under market, force appreciation, refinance, repeat. It weights gross rental yield 35%, entry price against a $100K capital base 15%, landlord-friendliness 15%, equity growth 15%, property-tax drag 10%, and climate/insurance risk 10%.</p>
<h2>Sources</h2>
<p>Home values are Zillow Home Value Index (ZHVI) metro figures and rents are Zillow Observed Rent Index (ZORI) metro figures, {{ vintage }}. Supporting context: US Census ACS, HUD Fair Market Rents, state landlord-tenant statutes, Tax Foundation effective property-tax tables. Landlord-friendliness, growth, and climate factors are editorial scores on public data, reviewed {{ today }}.</p>
<h2>What it is not</h2>
<p>Metro averages start the conversation; the block and the deal finish it. The Star Score is research and education, not investment advice, an appraisal, or a substitute for local underwriting.</p>"""

QUIZ_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › Find your market</nav>
<h1>Find your first (or next) market in 5 taps</h1>
<p class="lede">Answer five questions and get your three best-fit markets from {{ total }} tracked metros — plus a plan matched to how you want to operate. Free, no signup to see results.</p>
<div id="quiz">
<div class="explain"><b>1 · Capital to deploy</b><br>
<label><input type="radio" name="cap" value="50"> Under $50K</label><br>
<label><input type="radio" name="cap" value="120" checked> $50K–$150K</label><br>
<label><input type="radio" name="cap" value="300"> $150K+</label></div>
<div class="explain"><b>2 · What matters most</b><br>
<label><input type="radio" name="goal" value="cash" checked> Monthly cash flow</label><br>
<label><input type="radio" name="goal" value="bal"> Balanced</label><br>
<label><input type="radio" name="goal" value="growth"> Long-term equity growth</label></div>
<div class="explain"><b>3 · Where</b><br>
<label><input type="radio" name="where" value="any" checked> Anywhere the numbers work</label><br>
<label><input type="radio" name="where" value="state"> Near me: <select id="mystate"></select></label></div>
<div class="explain"><b>4 · The rehab</b><br>
<label><input type="radio" name="rehab" value="diy"> I'll do the work myself</label><br>
<label><input type="radio" name="rehab" value="crew" checked> I'll need a contractor crew</label><br>
<label><input type="radio" name="rehab" value="turnkey"> Hands-off / turnkey</label></div>
<div class="explain"><b>5 · Financing</b><br>
<label><input type="radio" name="fin" value="cash"> Cash</label><br>
<label><input type="radio" name="fin" value="pre"> Pre-approved</label><br>
<label><input type="radio" name="fin" value="need" checked> I'll need a lender</label></div>
<button onclick="quizGo()">Show my markets</button>
</div>
<div id="quiz-out"></div>
<script>
var MK = {{ markets_json }};
var ST = [...new Set(MK.map(m=>m.state))].sort();
document.getElementById("mystate").innerHTML = ST.map(s=>"<option>"+s+"</option>").join("");
function quizGo(){
 var v=n=>document.querySelector("input[name="+n+"]:checked").value;
 var cap=+v("cap")*1000, goal=v("goal"), wh=v("where"), rehab=v("rehab"), fin=v("fin");
 var pool=MK.filter(m=>m.v*0.25<=Math.max(cap,30000)*1.1);
 if(wh=="state"){var st=document.getElementById("mystate").value; var loc=pool.filter(m=>m.state==st); if(loc.length)pool=loc;}
 pool.sort((a,b)=> goal=="cash" ? b.y-a.y : goal=="growth" ? b.g-a.g : b.s-a.s);
 var picks=pool.slice(0,3);
 var why = goal=="cash"?"highest gross yields your budget reaches":goal=="growth"?"strongest 5-year equity growth in your range":"best overall Star Scores in your range";
 var html="<h2>Your three markets ("+why+")</h2>";
 picks.forEach(function(m,i){html+="<div class='explain'><b>"+(i+1)+" · <a href='{{ base }}/rentals/"+m.slug+"/'>"+m.name+", "+m.state+"</a></b> — Star Score "+m.s+", "+m.y+"% gross yield, typical home $"+m.v.toLocaleString()+". <a href='{{ base }}/rentals/"+m.slug+"/living/'>Living context</a></div>";});
 var plan="<h2>Your plan</h2><ul style='margin:8px 0 8px 20px;font-size:14.5px'>";
 plan+= rehab=="diy"?"<li>DIY rehab: budget with the <a href='{{ base }}/rentals/brrrr-calculator/'>calculator</a>'s cosmetic tiers and add 20% contingency — solo timelines slip.</li>":rehab=="crew"?"<li><b>Contractor route:</b> get three bids before you offer. We can introduce vetted investor-friendly crews in your market as we onboard them.</li>":"<li><b>Turnkey route:</b> prioritize metros with deep property-management infrastructure (Memphis, Birmingham, Cleveland score highest here).</li>";
 plan+= fin=="need"?"<li><b>Financing:</b> DSCR lenders qualify the property's rent, not your W-2 — typically 20-25% down. We can connect you with investor lenders active in these markets.</li>":fin=="cash"?"<li>Cash buyer: you're the fastest closer in the room — that's worth 5-10% on price. Refinance after stabilizing to redeploy.</li>":"<li>Pre-approved: confirm your lender allows the cash-out refi timeline BRRRR needs (seasoning rules vary).</li>";
 plan+="<li>Stress-test your first deal in the <a href='{{ base }}/rentals/brrrr-calculator/'>BRRRR calculator</a> before you offer.</li></ul>";
 var capture = {{ "true" if form_endpoint else "false" }} ?
  "<div class='explain'><b>Get this plan + weekly Star Opportunities for your markets</b><br><form action='{{ form_endpoint }}' method='POST' style='margin-top:6px'><input type='email' name='email' required placeholder='you@email.com' style='padding:9px;border:1px solid var(--line);border-radius:4px;width:60%'><input type='hidden' name='segments' id='seg'><button type='submit' style='margin-left:6px'>Send it</button></form></div>"
  : "<div class='explain'><b>Alerts for your markets are coming online now.</b> Founding-member pricing on the full toolkit: <a href='{{ base }}/pro/'>see Pro</a>.</div>";
 document.getElementById("quiz-out").innerHTML=html+plan+capture;
 var seg=document.getElementById("seg"); if(seg) seg.value=[goal,rehab,fin,picks.map(p=>p.slug).join("|")].join(",");
 document.getElementById("quiz-out").scrollIntoView({behavior:"smooth"});
}
</script>"""

PRO_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › Pro</nav>
<h1>Every market. Every layer. One simple unlock.</h1>
<p class="lede">Free gets you full depth on the top 15 markets and core data on all {{ total }}. Pro unlocks the intelligence layer on everything — and it's priced for one truth: a single good deal pays for decades of this.</p>
<table><tr><th></th><th>Free</th><th>Pro</th></tr>
<tr><td>Market pages, rankings, living guides, map</td><td>All {{ total }}</td><td>All {{ total }}</td></tr>
<tr><td>Full Star Score factor breakdowns</td><td>Top 15</td><td>All {{ total }}</td></tr>
<tr><td>BRRRR &amp; rehab calculator</td><td>✔</td><td>✔</td></tr>
<tr><td>Star Opportunity deal alerts (as markets onboard)</td><td>—</td><td>✔</td></tr>
<tr><td>Zip-level scores (rolling out)</td><td>—</td><td>✔</td></tr>
<tr><td>Quarterly rankings deep-report + data export</td><td>—</td><td>✔</td></tr></table>
{% if stripe_annual %}<p style="margin-top:16px"><a href="{{ stripe_annual }}"><button>Founding member — $290/yr (first 20, locked for life)</button></a></p>
{% if stripe_pass %}<p><a href="{{ stripe_pass }}"><button class="secondary" style="background:transparent;color:var(--ink)">7-day pass — $29</button></a></p>{% endif %}
{% else %}<div class="explain"><b>Founding membership opens this week</b> — the first 20 members lock $290/yr for life (then $390). Pick your markets meanwhile with the <a href="{{ base }}/start/">market finder</a>.</div>{% endif %}
<p class="quick">Fair-dealing note: core market data on every page stays free forever — Pro is the tooling on top, not a ransom on public data.</p>"""

GUIDE_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › BRRRR guide</nav>
<h1>What is the BRRRR strategy? The rental snowball, explained</h1>
<p class="lede">BRRRR stands for <b>Buy, Rehab, Rent, Refinance, Repeat</b>: buy a house below its fixed-up value, renovate it, rent it out, then refinance at the new higher value to pull most of your cash back out — so the same money buys the next house while you keep the first. Done well, one pot of capital compounds into a portfolio; that is the snowball.</p>
<h2>The five steps in plain English</h2>
<table><tr><th>Step</th><th>What it means</th></tr>
<tr><td><b>Buy</b></td><td>Pay less than the home will be worth after repairs (the "ARV"). The discount is where your profit is born — target all-in (price + rehab) at 75% of ARV or better.</td></tr>
<tr><td><b>Rehab</b></td><td>Renovate to rent-ready. See per-market cost rules of thumb on each metro page.</td></tr>
<tr><td><b>Rent</b></td><td>Place a tenant. The rent must cover the future loan with room to spare.</td></tr>
<tr><td><b>Refinance</b></td><td>A lender appraises the fixed-up home and loans ~75% of its new value, returning most of your cash.</td></tr>
<tr><td><b>Repeat</b></td><td>Redeploy that cash into the next house. Equity stays behind and compounds.</td></tr></table>
<h2>The three numbers that matter</h2>
<p><b>Price-to-rent ratio</b> — home price ÷ a year of rent. Under ~15 favors landlords; our <a href="{{ base }}/rentals/best-rental-markets-2026/">rankings</a> live mostly in the 13–16 range. <b>Gross yield</b> — a year of rent as a % of price, before expenses (a 50% expense rule is a sane planning default). <b>The 1% rule</b> — monthly rent of at least 1% of purchase price is the classic screen for cash flow.</p>
<h2>Where the Star Score fits</h2>
<p>The <a href="{{ base }}/methodology/">Star Score</a> ranks metros for this exact loop: yield, entry prices a normal budget can buy, landlord law, equity growth, taxes and insurance risk. Pick a market from the <a href="{{ base }}/">map</a>, then pressure-test your first deal in the <a href="{{ base }}/rentals/brrrr-calculator/">calculator</a>.</p>"""

LIFE_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › <a href="{{ base }}/rentals/{{ m.slug }}/">{{ m.name }}</a> › Living</nav>
<h1>Living in {{ m.name }}, {{ m.state }} ({{ year }}): economy, work &amp; what renters pay</h1>
<p class="lede">The {{ m.name }} metro is home to <b>{{ "{:,}".format(c.population) }}</b> people ({{ trend_txt }}), with a median household income of <b>${{ "{:,}".format(c.income) }}</b>. Typical rent of ${{ "{:,}".format(m.rent) }}/month works out to <b>{{ afford }}%</b> of the median household income — {{ afford_txt }} (Census ACS + Zillow, {{ vintage }}).</p>
<h2>Who works here: industry mix</h2>
<p>The share of {{ m.name }}'s workforce by sector — the base of tenant demand:</p>
<table><tr><th>Sector</th><th class="n">% of workforce</th></tr>
{% for label, pct in industries %}<tr><td>{{ label }}</td><td class="n">{{ pct }}%</td></tr>
{% endfor %}</table>
<p>{{ industry_read }}</p>
<h2>What this means for renters and landlords</h2>
<p>{{ takeaway }} Market pricing, yields and the Star Score live on the <a href="{{ base }}/rentals/{{ m.slug }}/">{{ m.name }} market page</a>; run a deal in the <a href="{{ base }}/rentals/brrrr-calculator/">calculator</a>.</p>
<div class="faq"><h2>Frequently asked questions</h2>
<h3>What salary do you need to rent comfortably in {{ m.name }}?</h3>
<p>At the 30%-of-income affordability rule, typical rent of ${{ "{:,}".format(m.rent) }}/month suggests a household income around ${{ "{:,}".format(need) }}/year. The metro's median household income is ${{ "{:,}".format(c.income) }}.</p>
<h3>What are the biggest industries in {{ m.name }}?</h3>
<p>{{ ind_answer }}</p>
</div>"""

STATE_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › <a href="{{ base }}/rentals/best-rental-markets-2026/">Rankings</a> › {{ state }}</nav>
<h1>Best rental markets in {{ state_name }} ({{ year }})</h1>
<p class="lede">{{ top.m.name }} is the highest-scoring rental market in {{ state_name }}, with a Star Score of <b>{{ top.score }}/100</b> and a gross yield of {{ top.yield_pct }}% on a typical home value of ${{ "{:,}".format(top.m.home_value) }} ({{ vintage }} data). {{ count }} {{ state_name }} metro{{ "s" if count > 1 }} rank among the top US markets tracked.</p>
<table><tr><th>#</th><th>Market</th><th class="n">Home value</th><th class="n">Rent/mo</th><th class="n">Yield</th><th class="n">Star Score</th></tr>
{% for r in rows %}<tr><td>{{ loop.index }}</td><td><a href="{{ base }}/rentals/{{ r.m.slug }}/">{{ r.m.name }}</a></td><td class="n">${{ "{:,}".format(r.m.home_value) }}</td><td class="n">${{ "{:,}".format(r.m.rent) }}</td><td class="n">{{ r.yield_pct }}%</td><td class="n">{{ r.score }}</td></tr>
{% endfor %}</table>"""

CALC_BODY = """
<nav class="crumbs"><a href="{{ base }}/">Atlas</a> › Calculator</nav>
<h1>BRRRR deal &amp; rehab cost calculator</h1>
<p class="lede">Estimate a renovation budget, then see whether a deal "snowballs" — whether refinancing at 75% of the after-repair value returns your cash so it can buy the next house. Cash flow uses the 50% expense rule; every output is an estimate for planning, not a bid or an appraisal.</p>
<h2>1 · Rough rehab budget</h2>
<div class="cgrid">
<div class="field"><label>House size (sq ft)</label><input id="sqft" type="number" value="1400"></div>
<div class="field"><label>Scope</label><select id="tier"><option value="20">Paint &amp; refresh ($15–25/sqft)</option><option value="35" selected>Cosmetic full ($25–45/sqft)</option><option value="60">Full renovation ($45–75/sqft)</option><option value="95">Gut ($75–120/sqft)</option></select></div>
</div>
<p class="quick" id="rehab-out"></p>
<h2>2 · The deal</h2>
<div class="cgrid">
<div class="field"><label>Purchase price ($)</label><input id="price" type="number" value="95000"></div>
<div class="field"><label>Rehab budget ($)</label><input id="rehab" type="number" value="49000"></div>
<div class="field"><label>After-repair value ($)</label><input id="arv" type="number" value="185000"></div>
<div class="field"><label>Monthly rent ($)</label><input id="rent" type="number" value="1450"></div>
<div class="field"><label>Refi rate (%)</label><input id="rate" type="number" step="0.1" value="7.5"></div>
<div class="field"><label>Your capital ($)</label><input id="cash" type="number" value="100000"></div>
</div>
<div id="rows"></div><div class="verdict" id="v"></div>
<script>
function n(id){return +document.getElementById(id).value||0}
function fm(x){return "$"+Math.round(x).toLocaleString()}
function calc(){
 var t=n("tier"),s=n("sqft");document.getElementById("rehab-out").innerHTML="Estimated budget: <b>"+fm(s*t*0.75)+" – "+fm(s*t*1.25)+"</b> (drop this into the deal below)";
 var P=n("price"),R=n("rehab"),A=n("arv"),rent=n("rent"),rate=n("rate")/100,cash=n("cash");
 var allIn=P+R,loan=A*0.75,leftIn=Math.max(0,allIn-loan),eq=A-loan;
 var i=rate/12,pmt=loan>0?loan*(i*Math.pow(1+i,360))/(Math.pow(1+i,360)-1):0;
 var cf=rent*0.5-pmt,doors=leftIn>0?Math.floor(cash/leftIn):99;
 document.getElementById("rows").innerHTML="<table><tr><td>All-in (buy+rehab)</td><td class=n>"+fm(allIn)+"</td></tr><tr><td>Refi loan (75% of ARV)</td><td class=n>"+fm(loan)+"</td></tr><tr><td>Cash left in deal</td><td class=n>"+fm(leftIn)+"</td></tr><tr><td>Equity kept</td><td class=n>"+fm(eq)+"</td></tr><tr><td>Monthly cash flow (50% rule)</td><td class=n>"+(cf>=0?"+":"−")+fm(Math.abs(cf))+"</td></tr></table>";
 var v=document.getElementById("v");
 if(allIn>A*0.78){v.className="verdict bad";v.innerHTML="<b>Doesn&rsquo;t snowball.</b> All-in is "+Math.round(allIn/A*100)+"% of ARV, trapping "+fm(leftIn)+" per door — "+fm(cash)+" supports only "+doors+" door(s). Target 75% of ARV all-in.";}
 else if(cf<0){v.className="verdict bad";v.innerHTML="<b>Equity works, cash flow doesn&rsquo;t.</b> Runs "+fm(Math.abs(cf))+"/mo negative — need higher rent, cheaper debt, or a bigger discount.";}
 else{v.className="verdict";v.innerHTML="<b>This snowballs.</b> Each cycle leaves "+fm(leftIn)+" behind and returns the rest — "+fm(cash)+" supports ~<b>"+(doors>=99?"an open-ended chain of":doors)+" doors</b>, each holding "+fm(eq)+" equity and paying ~"+fm(Math.max(0,cf))+"/mo.";}}
["sqft","tier","price","rehab","arv","rent","rate","cash"].forEach(function(id){document.getElementById(id).addEventListener("input",calc)});calc();
</script>"""

env = Environment(loader=DictLoader({
    "base": BASE, "metro": METRO_BODY, "rankings": RANKINGS_BODY,
    "compare": COMPARE_BODY, "index": INDEX_BODY, "method": METHOD_BODY,
    "calc": CALC_BODY, "guide": GUIDE_BODY, "state": STATE_BODY, "life": LIFE_BODY, "quiz": QUIZ_BODY, "pro": PRO_BODY,
}))


STATE_NAMES = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","DC":"Washington DC"}

def page(path, title, description, body_html, jsonld=None):
    full = env.get_template("base").render(
        title=title, description=description, body=body_html,
        canonical=f"{BASE_URL}{path}", base=BASE_URL, today=TODAY,
        vintage=DATA_VINTAGE, jsonld=[json.dumps(x) for x in (jsonld or [])])
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(full)
    return path


US_OUTLINE = [(48.4,-124.7),(46.2,-124.0),(42.0,-124.4),(40.4,-124.4),(38.9,-123.7),
 (37.8,-122.5),(36.6,-121.9),(34.4,-120.5),(33.7,-118.3),(32.5,-117.1),(32.5,-114.8),
 (31.3,-111.1),(31.8,-106.5),(29.5,-104.4),(29.3,-103.3),(26.0,-97.5),(27.8,-97.2),
 (29.7,-93.8),(29.2,-90.1),(30.4,-87.3),(29.7,-84.9),(27.8,-82.6),(25.2,-80.9),
 (25.5,-80.1),(28.5,-80.6),(30.7,-81.4),(32.0,-80.8),(33.9,-78.0),(35.2,-75.5),
 (36.9,-76.0),(38.9,-75.1),(40.5,-74.0),(41.3,-71.9),(41.7,-70.0),(43.1,-70.6),
 (44.8,-66.9),(47.4,-68.3),(45.0,-71.5),(45.0,-74.7),(44.1,-76.5),(43.3,-79.0),
 (42.3,-81.0),(41.7,-83.5),(43.6,-82.5),(45.8,-84.7),(46.5,-84.4),(47.5,-89.6),
 (48.0,-89.5),(49.0,-95.2),(49.0,-123.1)]

def _proj(lat, lng, W=944, H=520, P=16):
    x = P + ((lng + 125) / (125 - 66)) * (W - 2 * P)
    y = P + ((49.5 - lat) / (49.5 - 24.5)) * (H - 2 * P)
    return x, y

def svg_map(ranked, refs):
    d = " ".join(("M" if i == 0 else "L") + f"{_proj(a,b)[0]:.0f} {_proj(a,b)[1]:.0f}"
                 for i, (a, b) in enumerate(US_OUTLINE)) + " Z"
    marks = []
    for r in sorted(ranked + refs, key=lambda x: x["score"]):
        m = r["m"]
        if m.lat is None or m.lng is None:
            continue
        x, y = _proj(m.lat, m.lng)
        if getattr(m, "ref", False) or m.slug in ("austin-tx","denver-co","chicago-il"):
            marks.append(f'<a href="{BASE_URL}/rentals/{m.slug}/"><circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="#8FA3A8"><title>{m.name}: reference market</title></circle></a>')
        else:
            sz = 14 + r["score"] / 100 * 22
            marks.append(f'<a href="{BASE_URL}/rentals/{m.slug}/"><text x="{x:.0f}" y="{y + sz*0.36:.0f}" text-anchor="middle" font-size="{sz:.0f}" fill="#C08A1E" font-weight="700">\u2605<title>{m.name}: Star Score {r["score"]}</title></text></a>')
    return (f'<svg viewBox="0 0 944 520" role="img" aria-label="Map of US BRRRR rental markets by Star Score">'
            f'<path d="{d}" fill="#1E4E49" fill-opacity="0.13" stroke="#1E4E49" stroke-opacity="0.55" stroke-width="1.5" stroke-linejoin="round"/>'
            + "".join(marks) + "</svg>")

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
    global DATA_VINTAGE
    dm = raw[0].get("data_month") if raw else None
    if dm:
        DATA_VINTAGE = datetime.date.fromisoformat(dm).strftime("%B %Y")
        print(f"[build] data vintage: {DATA_VINTAGE}")
    metros = []
    for r in raw:
        m = dict(r)
        for k in ("home_value", "rent", "landlord", "growth", "climate"):
            m[k] = int(float(m[k]))
        for k in ("tax_rate",):
            m[k] = float(m[k])
        for k in ("lat", "lng"):
            m[k] = float(m[k]) if str(m[k]).strip() else None
        m["ratio_raw"] = m["home_value"] / (m["rent"] * 12)
        m["ref"] = m["ratio_raw"] >= 19  # rent-lean reference tier
        if not m.get("blurb"):
            y = m["rent"] * 12 / m["home_value"] * 100
            m["blurb"] = (f"The {m['name']} metro posts a price-to-rent ratio of "
                f"{round(m['ratio_raw']) if 'ratio_raw' in m else round(m['home_value']/(m['rent']*12))} "
                f"on a typical home value of ${m['home_value']:,} and typical rent of ${m['rent']:,}/month "
                f"— a gross rental yield of {y:.1f}% before expenses. Factor scores below show how it "
                "stacks up on landlord law, taxes, growth and risk.")
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
        brrrr_answer = (
            f"With a typical home at ${m.home_value:,} and rent of ${m.rent:,}/month "
            f"({r['yield_pct']}% gross yield), {m.name} "
            + ("suits the BRRRR strategy well: entry prices leave room to buy below market, renovate, and refinance without trapping capital."
               if r['yield_pct'] >= 6.5 and m.home_value < 300000 else
               "can work for BRRRR in select submarkets, but higher prices or thinner yields mean deals need bigger discounts to snowball."))
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
                "text": f"{r['ratio']}, based on a typical home value of ${m.home_value:,} and typical rent of ${m.rent:,}/month."}},
            {"@type": "Question",
             "name": f"Is {m.name} a good BRRRR market in {year}?",
             "acceptedAnswer": {"@type": "Answer", "text": brrrr_answer}}]}
        ds_ld = {"@context": "https://schema.org", "@type": "Dataset",
                 "name": f"{m.name} rental market metrics {year}",
                 "description": f"Home value, rent, price-to-rent ratio and Star Score for the {m.name}, {m.state} metro.",
                 "temporalCoverage": str(year),
                 "creator": {"@type": "Organization", "name": "Snowball Atlas"}}
        body = env.get_template("metro").render(
            m=m, base=BASE_URL, year=year, vintage=DATA_VINTAGE,
            ratio=r["ratio"], yield_pct=r["yield_pct"], score=r["score"],
            star_str=r["star_str"], rank=rank, total=total,
            factors=r["factors"], compares=compares, verdict=verdict,
            brrrr_answer=brrrr_answer, unlocked=(rank <= 15 or r not in ranked))
        urls.append(page(
            f"/rentals/{m.slug}/",
            f"{m.name}, {m.state} BRRRR & Rental Market Data {year}: Prices, Rents, Star Score",
            f"{m.name} rental market {year}: typical home ${m.home_value:,}, rent ${m.rent:,}/mo, price-to-rent {r['ratio']}, Star Score {r['score']}/100.",
            body, [faq_ld, ds_ld]))

    # --- comparison pages (top 10 pairs)
    for a, b in itertools.combinations(ranked[:15], 2):
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
        f"Best BRRRR & Cash-Flow Rental Markets in the US ({year}), Ranked by Star Score",
        f"{total} US metros ranked for cash-flow rental investing on {DATA_VINTAGE} Zillow data. {top['m'].name} leads at {top['score']}/100.",
        body))

    # --- living pages (only when the Census context pipeline has run)
    ctx_path = os.path.join(ROOT, "data", "metro_context.csv")
    ctx = {}
    if os.path.exists(ctx_path):
        for row in csv.DictReader(open(ctx_path)):
            ctx[row["slug"]] = row
    for r in everything:
        m = r["m"]
        cr = ctx.get(m.slug)
        if not cr:
            continue
        c = type("C", (), {"population": int(cr["population"]),
                           "income": int(cr["income"])})()
        trend = cr.get("pop_5yr_pct")
        trend_txt = (f"up {trend}% over five years" if trend and float(trend) > 0
                     else f"down {abs(float(trend))}% over five years" if trend
                     else "population trend unavailable")
        afford = round(m.rent * 12 / c.income * 100, 1)
        afford_txt = ("comfortably below the 30% affordability threshold"
                      if afford < 25 else
                      "near the 30% affordability threshold" if afford <= 32
                      else "above the 30% affordability threshold, a strain signal")
        need = round(m.rent * 12 / 0.30 / 1000) * 1000
        industries = [(cr[f"ind{i}"], cr[f"ind{i}_pct"]) for i in range(1, 6)
                      if cr.get(f"ind{i}")]
        top_label = industries[0][0] if industries else ""
        industry_read = (f"{top_label} is the metro's largest employment base"
                         + (" — sectors like education and health care are recession-resilient anchors for rental demand."
                            if "health" in top_label.lower() or "Education" in top_label
                            else "; a diversified mix beneath it spreads tenant-demand risk."))
        takeaway = (f"Rents at {afford}% of median income leave "
                    + ("room for rent growth without pricing out the median tenant."
                       if afford < 25 else
                       "moderate headroom; underwrite rent growth conservatively."
                       if afford <= 32 else
                       "little headroom — expect tenant price sensitivity."))
        ind_answer = ("By workforce share: "
                      + ", ".join(f"{l} ({p}%)" for l, p in industries[:3])
                      + " (Census ACS 5-year).")
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question",
             "name": f"What salary do you need to rent comfortably in {m.name}?",
             "acceptedAnswer": {"@type": "Answer",
                "text": f"About ${need:,}/year at the 30% rule, against typical rent of ${m.rent:,}/month; median household income is ${c.income:,}."}},
            {"@type": "Question",
             "name": f"What are the biggest industries in {m.name}?",
             "acceptedAnswer": {"@type": "Answer", "text": ind_answer}}]}
        body = env.get_template("life").render(
            m=m, c=c, base=BASE_URL, year=year, vintage=DATA_VINTAGE,
            trend_txt=trend_txt, afford=afford, afford_txt=afford_txt,
            need=need, industries=industries, industry_read=industry_read,
            takeaway=takeaway, ind_answer=ind_answer)
        urls.append(page(
            f"/rentals/{m.slug}/living/",
            f"Living in {m.name}, {m.state} ({year}): Economy, Industries & Rent Affordability",
            f"{m.name} living guide for renters and investors: population {c.population:,}, median income ${c.income:,}, rent-to-income {afford}%, top industries from Census data.",
            body, [faq_ld]))

    # --- state pages
    by_state = {}
    for r in ranked:
        by_state.setdefault(r["m"].state, []).append(r)
    for st, rows in sorted(by_state.items()):
        if len(rows) < 1:
            continue
        sname = STATE_NAMES.get(st, st)
        sslug = sname.lower().replace(" ", "-")
        body = env.get_template("state").render(
            rows=rows, top=rows[0], count=len(rows), state=st, state_name=sname,
            base=BASE_URL, year=year, vintage=DATA_VINTAGE)
        urls.append(page(
            f"/rentals/state/{sslug}/",
            f"Best Rental Markets in {sname} ({year}): Star Score Rankings",
            f"{sname} rental markets ranked for cash-flow and BRRRR investing on {DATA_VINTAGE} data. {rows[0]['m'].name} leads at {rows[0]['score']}/100.",
            body))

    # --- index + methodology
    body = env.get_template("index").render(
        rows=ranked, top=top, total=total, base=BASE_URL, vintage=DATA_VINTAGE,
        map_svg=svg_map(ranked, refs))
    urls.append(page("/", f"Snowball Atlas: US Rental Markets Ranked by Star Score",
                     f"US rental markets scored 0-100 for buy-refinance-repeat investing. {top['m'].name} currently leads at {top['score']}/100.",
                     body))
    mjson = json.dumps([{"slug": x["m"].slug, "name": x["m"].name,
                          "state": x["m"].state, "v": x["m"].home_value,
                          "y": x["yield_pct"], "g": x["factors"]["growth"]["score"],
                          "s": x["score"]} for x in ranked])
    urls.append(page("/start/", "Find Your Rental Market in 5 Taps",
                     "Answer five questions — capital, goals, location, rehab style, financing — and get your three best-fit US rental markets instantly.",
                     env.get_template("quiz").render(base=BASE_URL, total=total,
                         markets_json=mjson, form_endpoint=FORM_ENDPOINT)))
    urls.append(page("/pro/", "Snowball Atlas Pro: Unlock Every Market",
                     "Free covers core data on all markets and full depth on the top 15. Pro unlocks factor breakdowns, deal alerts and zip-level scores everywhere.",
                     env.get_template("pro").render(base=BASE_URL, total=total,
                         stripe_annual=STRIPE_ANNUAL, stripe_pass=STRIPE_PASS)))
    urls.append(page("/rentals/brrrr-guide/",
                     f"What Is the BRRRR Strategy? Beginner's Guide ({year})",
                     "BRRRR means Buy, Rehab, Rent, Refinance, Repeat — the rental snowball strategy explained in plain English, with the three numbers that matter.",
                     env.get_template("guide").render(base=BASE_URL)))
    urls.append(page("/rentals/brrrr-calculator/",
                     f"BRRRR Deal & Rehab Cost Calculator ({year})",
                     "Estimate renovation costs by square foot and scope, then test whether a BRRRR deal returns your capital at a 75% refinance.",
                     env.get_template("calc").render(base=BASE_URL)))
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
- [BRRRR guide]({BASE_URL}/rentals/brrrr-guide/): the Buy-Rehab-Rent-Refinance-Repeat strategy explained
- [BRRRR & rehab calculator]({BASE_URL}/rentals/brrrr-calculator/): deal and renovation cost estimates
{chr(10).join(f"- [{r['m'].name}]({BASE_URL}/rentals/{r['m'].slug}/): Star Score {r['score']}, yield {r['yield_pct']}%" for r in ranked[:5])}

Citation format: "According to Snowball Atlas's Star Score index ({year}), ..."
""")
    print(f"[build] {len(urls)} pages -> {OUT}")


if __name__ == "__main__":
    main()
