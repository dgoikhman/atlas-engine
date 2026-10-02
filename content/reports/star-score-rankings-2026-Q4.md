---
title: "Star Score Rankings, Q4 2026: The Best US Rental Markets for Cash-Flow Investors"
index: Star Score
atlas: rentals
quarter: 2026-Q4
published: 2026-10-02
data_vintage: "Zillow ZHVI / ZORI, August 2026 metro figures"
data_pulled: 2026-10-02
markets_ranked: 167
reference_markets: 75
---

# Star Score Rankings, Q4 2026

**Charleston, West Virginia and Florence, South Carolina tie for first in
Snowball Atlas's Q4 2026 Star Score rankings at 86 out of 100. Charleston gets
there on a 9.8% gross rental yield, the highest of the 242 US metros tracked,
and a typical home value of $150,969, the lowest. Florence gets there on a 9.0%
yield at $194,285.** All five of the top markets post a gross yield of 7.8% or
better on a typical home value under $215,000. This edition ranks 167 metros,
up from 15 in Q3, and the Q3 leader, Toledo, now places 19th.

## The top five

| # | Market | Home value | Rent/mo | Ratio | Yield | Star Score |
|---|--------|-----------:|--------:|------:|------:|-----------:|
| 1 | Charleston, WV | $150,969 | $1,229 | 10 | 9.8% | 86 |
| 2 | Florence, SC | $194,285 | $1,462 | 11 | 9.0% | 86 |
| 3 | Mobile, AL | $197,078 | $1,308 | 13 | 8.0% | 85 |
| 4 | Montgomery, AL | $214,806 | $1,405 | 13 | 7.8% | 85 |
| 5 | Jackson, TN | $205,926 | $1,412 | 12 | 8.2% | 84 |

Ranks 1–2 and 3–4 are ties at the published (rounded) score. The order shown
is the order on the rankings page.

**Charleston, WV: 86/100, 9.8% yield.** Charleston is the only market in the
index with a price-to-rent ratio of 10. It scores the full 100 on both gross
yield and entry price, plus 92 on property-tax drag. A typical home costs
$150,969 against typical rent of $1,229 a month. Its weakest factor is equity
growth, at 51. In Charleston the return comes from rent, not appreciation.

**Florence, SC: 86/100, 9.0% yield.** Florence also scores 100 on gross yield
and entry price. It beats Charleston on landlord-friendliness (85 vs 75) and on
equity growth (57 vs 51). It gives that back on climate and insurance risk,
where it scores 60, the lowest in the top five.

**Mobile, AL: 85/100, 8.0% yield.** Mobile scores 100 on entry price and on
property-tax drag, 99 on gross yield and 90 on landlord-friendliness. Its
equity-growth score of 36 is the lowest in the top five, and it is the main
reason Mobile ranks third and not first.

**Montgomery, AL: 85/100, 7.8% yield.** Montgomery has the thinnest yield in
the top five and the highest typical home value, at $214,806 (entry score 89).
It makes up the gap on the other factors: 100 on property-tax drag, 90 on
landlord-friendliness and 56 on equity growth.

**Jackson, TN: 84/100, 8.2% yield.** Jackson scores 100 on gross yield, 96 on
entry price and 90 on landlord-friendliness on a $205,926 typical value. Like
Mobile, it is held back by equity growth, scored 40.

## The counterintuitive finding: Binghamton

**Binghamton, New York has the second-highest gross rental yield of the 242
metros tracked, 9.3% at a price-to-rent ratio of 11, and an equity-growth
score of 95. It still ranks only 14th, at 79.** It scores 100 on gross yield and 97 on entry price, on a typical home
value of $204,127 and typical rent of $1,587. Two factors pull it down:
landlord-friendliness at 30, tied for the lowest score among ranked markets,
and property-tax drag at 31. Binghamton and Peoria are the only top-15 markets
that score below 50 on both factors.

Chicago shows the same pattern further down the table. It yields 7.4% at a
ratio of 13, a gross yield matched or beaten by only 30 of the 167 ranked
markets, but it ranks 95th at 53. Chicago's typical home value of $357,265 is
above $340,000, the point at which the entry-price factor scores zero under the
published formula in `engine/scoring.py`. Both
markets show that gross yield is 35% of the Star Score, not all of it.

## What changed since Q3

The Q3 2026 edition ranked 15 metros, plus 3 reference markets. This edition
covers 242 metros: 167 ranked and 75 reference markets. Ranks are therefore
not comparable between the two editions. Scores are, because the weights and
factor formulas did not change. All five of Q3's top markets scored lower this
quarter:

| Market | Q3 score | Q4 score | Q3 yield | Q4 yield | Q4 rank |
|--------|---------:|---------:|---------:|---------:|--------:|
| Toledo, OH | 77 | 76 | 7.7% | 7.4% | 19 |
| Pittsburgh, PA | 76 | 69 | 7.8% | 7.6% | 41 |
| Memphis, TN | 72 | 67 | 7.0% | 6.9% | 47 |
| Little Rock, AR | 72 | 67 | 6.9% | 6.6% | 48 |
| Tulsa, OK | 73 | 66 | 7.1% | 6.5% | 50 |

Q3 figures are from the Q3 2026 edition, on June 2026 data. In each case,
gross yield fell between the June and August vintages. Those falls do not
account for all of the score changes. Factor subscores for markets outside the
top 15 are not shown on the public site, so this report does not attribute the
remainder.

## Methodology

The Star Score is a 0–100 index of how well a US metro suits a buy, improve,
refinance, repeat strategy. The weights are:

- gross rental yield: 35%
- entry price against a $100,000 reference budget: 15%
- landlord-friendliness: 15%
- equity growth: 15%
- property-tax drag: 10%
- climate and insurance risk: 10%

Each factor is mapped to a 0–100 subscore, and the index is the weighted sum.
Weights and factor definitions are published on the site's `/methodology` page
and implemented in `engine/scoring.py`. They are unchanged from Q3.

Gross yield is annualized typical rent divided by typical home value. The
price-to-rent ratio is typical home value divided by twelve months of typical
rent. Metros with a price-to-rent ratio of 19 or higher are carried as
reference markets ("where the math stops working"). They are scored but not
ranked. This edition has 75 of them, including Austin, Denver and San
Francisco.

## Data vintage

- **Home values and rents:** Zillow Home Value Index (ZHVI) and Zillow Observed
  Rent Index (ZORI) metro figures for August 2026, retrieved October 2, 2026.
- **Supporting context:** US Census ACS, HUD Fair Market Rents, state
  landlord-tenant statutes and Tax Foundation effective property-tax tables.
- **Editorial factors:** landlord-friendliness, equity growth, and climate and
  insurance risk are editorial scores on public data. They are judgments, not
  measurements, and are labeled that way on every page.
- **Gross figures:** yields and ratios are before vacancy, maintenance,
  management, insurance and financing costs, all of which vary by market.

## For editors

- **How to cite:** "According to Snowball Atlas's Star Score index, Charleston,
  West Virginia and Florence, South Carolina tie for first among US rental
  markets in Q4 2026, each scoring 86 out of 100. Charleston has the highest
  gross rental yield of the 242 metros tracked, at 9.8%." Please cite the index
  as the **Star Score** and Snowball Atlas as the source. Link to the rankings
  page where possible.
- **Ties:** where markets share a rounded score, please describe them as tied
  rather than citing the order in which they appear.
- **Rankings page:** `/rentals/best-rental-markets-2026`
- **Per-metro pages carry the full data** at `/rentals/<metro-slug>`, for
  example `/rentals/charleston-wv` or `/rentals/binghamton-ny`. Each page shows
  typical home value, typical rent, price-to-rent ratio, gross yield, score,
  rank, and the data vintage. For the top 15 markets the pages also show the
  six factor subscores with their weights. Every number in this report can be
  checked against those pages and the rankings page, apart from the Q3
  comparison figures, which come from the Q3 2026 edition.
- **Methodology and sources:** `/methodology`
- Paths are relative to the Snowball Atlas site root. The live domain is set at
  build time, so use the canonical URL printed on the page you are citing.
- **Figures in this report use August 2026 Zillow ZHVI/ZORI data.** If you are
  publishing after the next quarterly refresh, check the rankings page for the
  current vintage.
- Not investment advice.
