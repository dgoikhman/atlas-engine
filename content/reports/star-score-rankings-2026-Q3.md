---
title: "Star Score Rankings, Q3 2026: The US Rental Markets That Clear an 8% Gross Yield"
index: Star Score
atlas: rentals
quarter: 2026-Q3
published: 2026-09-10
data_vintage: "Zillow ZHVI / ZORI, July 2026 metro figures"
last_reviewed: 2026-09-10
markets_tracked: 242
markets_ranked: 165
reference_markets: 77
revision: 2
supersedes: "Q3 2026 edition published 2026-09-10 (15 markets ranked, June 2026 vintage)"
---

# Star Score Rankings, Q3 2026

**Florence, South Carolina leads Snowball Atlas's Q3 2026 Star Score rankings at
87 out of 100, on an 8.6% gross rental yield and a typical home value of
$193,768 as of July 2026.** Of the 242 US metros tracked this quarter, 165 are
ranked, and only 12 of them clear a gross yield of 8.0% — the median ranked
market yields 6.3% at a price-to-rent ratio of 16. Scores among ranked markets
run from Florence's 87 down to 29 for Redding, California, and the reference
tier bottoms out at 19 for San Francisco.

The top of the table is tight. Three markets are separated by less than half a
point before rounding, and all five leaders sit within 1.4 points of each other.
Every top-five market posts a gross yield of 7.9% or better at a price-to-rent
ratio of 13 or lower, and none of the top 20 carries a typical home value above
$255,173.

## The top five

| # | Market | Home value | Rent/mo | Ratio | Yield | Star Score |
|---|--------|-----------:|--------:|------:|------:|-----------:|
| 1 | Florence, SC | $193,768 | $1,395 | 12 | 8.6% | 87 |
| 2 | Montgomery, AL | $214,925 | $1,420 | 13 | 7.9% | 86 |
| 3 | Mobile, AL | $197,652 | $1,327 | 12 | 8.1% | 86 |
| 4 | Charleston, WV | $150,171 | $1,264 | 10 | 10.1% | 86 |
| 5 | Jackson, TN | $207,877 | $1,425 | 12 | 8.2% | 85 |

**1. Florence, SC — 87/100, 8.6% yield.** Florence is the only market to break
87, and it does it without a weak factor. It scores 100 on gross yield and 100
on entry price — a $193,768 typical value sits at the bottom of the entry band —
and adds 91 on property-tax drag and 85 on landlord-friendliness. Its softest
factors are climate and insurance risk at 60 and equity growth at 58, so
Florence ranks first on current rent rather than on expected appreciation.

**2. Montgomery, AL — 86/100, 7.9% yield.** Montgomery scores a full 100 on
property-tax drag, against Alabama's 0.40% state average effective rate, and 90
on landlord-friendliness. It is the most expensive market in the top five at
$214,925 and the only one that does not max out gross yield, scoring 98 on a
7.9% yield and 89 on entry price. Equity growth of 56 is mid-field.

**3. Mobile, AL — 86/100, 8.1% yield.** Mobile maxes four factors or comes
close: 100 on gross yield, 100 on entry price, 100 on property-tax drag and 90
on landlord-friendliness. It finishes behind Montgomery by 0.4 point before
rounding because of the two factors it does not win — equity growth of 38, the
lowest in the top five, and climate and insurance risk of 65, reflecting Gulf
Coast exposure.

**4. Charleston, WV — 86/100, 10.1% yield.** Charleston has the highest gross
yield and the lowest entry price of all 242 metros tracked: $1,264 of monthly
rent against a $150,171 typical value, a price-to-rent ratio of 10. It scores
100 on gross yield, 100 on entry price, 92 on property-tax drag and 80 on
climate and insurance risk, the best risk score in the top five.
Landlord-friendliness of 75 and equity growth of 48 hold it to fourth.

**5. Jackson, TN — 85/100, 8.2% yield.** Jackson pairs a maxed gross-yield
factor with 90 on landlord-friendliness and 94 on entry price at a $207,877
typical value. Property-tax drag scores 86 and climate and insurance risk 70.
Equity growth of 46 is what separates it from Florence.

## The counterintuitive finding: the highest yield in the index does not win it

**Charleston, West Virginia collects a 10.1% gross yield — the only double-digit
yield among 242 tracked metros, and 1.3 points clear of the next best, the 8.8%
posted by Shreveport and Monroe, Louisiana — and it ranks fourth, not first.**
The reason is that the Star Score's gross-yield factor saturates: the factor maps
a 4.5% yield to 0 and an 8.0% yield to 100, and everything above 8.0% also
scores 100. Four of the five leading markets — Florence, Mobile, Charleston and
Jackson — score an identical 100 on yield despite yields spanning 8.1% to 10.1%.
Charleston's 2.1 points of yield above the cap are invisible to the index, and
the remaining 65% of the weight decides the order.

The same effect runs the other way further down the table. Seventeen ranked
markets share a price-to-rent ratio of 13, and they span 32 points of Star
Score: Montgomery, Alabama at 86 and second overall, and Chicago, Illinois at 54
and 97th. Chicago's 7.5% gross yield would place it inside the top 30 on yield
alone, but its $360,262 typical home value is above the $340,000 ceiling of the
entry-price factor, so that factor scores 0. A headline ratio is not a rank.

For investors the practical reading is narrow: past a gross yield of about 8%,
this index stops paying for more yield and starts paying for entry price,
landlord law, taxes, appreciation and insurance risk. For anyone using the
ratio as a screen, 13 is not a finding on its own.

## Methodology

The Star Score is a 0-100 index of how well a US metro suits a buy, improve,
refinance, repeat strategy. It weights gross rental yield 35%, entry price
against a $100,000 capital base 15%, landlord-friendliness 15%, equity growth
15%, property-tax drag 10%, and climate and insurance risk 10%. Each factor maps
to a 0-100 subscore and the index is the weighted sum; the weights are published
at `/methodology` and the factor definitions are implemented in
`engine/scoring.py`. Three bands are worth stating because they drive the results
above: gross yield scores 0 at 4.5% and 100 at 8.0% and above; entry price scores
100 at a typical value of $200,000 or below and 0 at $340,000 or above;
property-tax drag scores 100 at an effective rate of 0.40% or below and 0 at
2.20% or above.

Two limitations matter when citing metro-level figures. Landlord-friendliness,
property-tax drag and climate and insurance risk are state-level inputs, so
metros in the same state carry identical subscores on those three factors —
Mobile and Montgomery differ only on gross yield, entry price and equity growth.
Equity growth is not an editorial judgment: it is each metro's five-year ZHVI
appreciation, July 2021 to July 2026, percentile-ranked within the tracked
cohort. Because it is a percentile, growth subscores re-baseline whenever the
cohort changes, and they describe relative, not absolute, appreciation.

Of the 242 metros tracked, 165 are ranked. The 77 metros with a price-to-rent
ratio of 19 or higher are carried as a reference tier to show the range of the
index rather than to recommend them. Displayed scores are rounded to whole
numbers while the ranking uses the unrounded score, which is why three markets
display 86 in different positions. Gross yield is annualized typical rent divided
by typical home value, and the price-to-rent ratio is typical home value divided
by twelve months of typical rent. Both are gross, before vacancy, maintenance,
management, insurance and financing costs, all of which are local.

## Data vintage

Home values are Zillow Home Value Index (ZHVI) metro figures and rents are
Zillow Observed Rent Index (ZORI) metro figures, both July 2026 — the most
recent vintage in the dataset behind this edition. Five-year growth is measured
against July 2021. Supporting context comes from the US Census ACS, HUD Fair
Market Rents, state landlord-tenant statutes and Tax Foundation effective
property-tax tables. The landlord-friendliness and climate and insurance risk
factors are editorial scores on public data, reviewed September 2026; they are
judgments, not measurements, and are labeled as such on every page.

## Revision note

This edition supersedes the Q3 2026 rankings published earlier on 2026-09-10,
which ranked 15 markets on June 2026 data. Scores and ranks are not comparable
between the two, for three reasons: tracked coverage went from 15 metros to 242;
equity growth is a within-cohort percentile, so it re-baselined when the cohort
grew; and the value and rent vintage moved from June to July 2026. A defect in
the ranking order was also corrected — the table had been sorted on the
display-rounded score, which left tied markets in source-data order.

Toledo, Ohio, which led the earlier edition at 77, still scores 77 and now ranks
19th of 165. Its score did not fall; the field around it grew. Because this is
the first edition on the 242-metro cohort, it reports no quarter-over-quarter
movement. Rank and score changes will be reported from Q4 2026 forward, against
this edition as the baseline.

## For editors

- **How to cite:** "According to Snowball Atlas's Star Score index, Florence,
  South Carolina ranks first among US rental markets in Q3 2026 with a score of
  87 out of 100 and an 8.6% gross rental yield." Please cite the index as the
  **Star Score** and Snowball Atlas as the source, with a link to the rankings
  page where possible.
- **Rankings page:** `/rentals/best-rental-markets-2026` — all 165 ranked
  markets plus the 77-metro reference tier, with home values and rents.
- **Per-metro pages carry the full data** — typical home value, typical rent,
  price-to-rent ratio, gross yield, rank, and the source and review dates — at
  `/rentals/<metro-slug>`, for example `/rentals/florence-sc` or
  `/rentals/chicago-il`. The six factor subscores with their weights are shown
  on the top 15 markets' pages. Every number in this report is reproducible
  from those pages.
- **Methodology and sources:** `/methodology`
- Paths above are relative to the Snowball Atlas site root; the live domain is
  set at build time via `BASE_URL`, so use the canonical URL printed on the page
  you are citing.
- **Figures in this report are as of July 2026 (Zillow ZHVI/ZORI), reviewed
  September 2026.** If you are publishing after the next quarterly refresh,
  check the rankings page for the current vintage.
- Not investment advice.
</content>
