---
title: "Star Score Rankings, Q3 2026: The Best US Rental Markets for Cash-Flow Investors"
index: Star Score
atlas: rentals
quarter: 2026-Q3
published: 2026-09-10
data_vintage: "Zillow ZHVI / ZORI, June 2026 metro figures"
last_reviewed: 2026-09-10
markets_ranked: 15
reference_markets: 3
---

# Star Score Rankings, Q3 2026

**Toledo, Ohio leads Snowball Atlas's Q3 2026 Star Score rankings at 77 out of
100, on a 7.7% gross rental yield and a typical home value of $204,000 — the
lowest entry price of the 15 US metros ranked.** Pittsburgh follows at 76 with
the highest gross yield in the index at 7.8%, and every market in the top five
posts a gross yield of 6.9% or better at a price-to-rent ratio of 15 or lower.
The spread across the index is wide: Denver scores 31 on a 4.1% yield, less
than half of Toledo's score.

## The top five

| # | Market | Home value | Rent/mo | Ratio | Yield | Star Score |
|---|--------|-----------:|--------:|------:|------:|-----------:|
| 1 | Toledo, OH | $204,000 | $1,302 | 13 | 7.7% | 77 |
| 2 | Pittsburgh, PA | $234,727 | $1,523 | 13 | 7.8% | 76 |
| 3 | Tulsa, OK | $220,000 | $1,300 | 14 | 7.1% | 73 |
| 4 | Memphis, TN | $246,954 | $1,435 | 14 | 7.0% | 72 |
| 5 | Little Rock, AR | $218,000 | $1,250 | 15 | 6.9% | 72 |

**1. Toledo, OH — 77/100, 7.7% yield.** Toledo wins on the two factors that
carry the most weight together. It scores 90 of 100 on gross yield and 97 on
entry price, the highest entry score in the index, because a $204,000 typical
home value leaves room for a downpayment and a rehab budget inside a $100,000
capital base. Its weak spot is equity growth, scored 45 — Toledo is a market
where the return arrives as rent, not appreciation.

**2. Pittsburgh, PA — 76/100, 7.8% yield.** The highest gross yield of the 18
metros in the index, at a $234,727 typical value and $1,523 typical rent, and a
gross-yield factor score of 94. Pittsburgh also carries the index's best
climate and insurance risk score at 90. It trails Toledo on entry price (75)
and, like Toledo, on growth (50): an eds-and-meds economy produces steady rent
checks and slow appreciation.

**3. Tulsa, OK — 73/100, 7.1% yield.** Tulsa is the first market in the table
where landlord law does the work. It scores 90 on landlord-friendliness against
Toledo's 75 and Pittsburgh's 70, and pairs that with a $220,000 typical value
and a 0.9% effective property-tax rate. Its climate and insurance risk score of
60 is the weakest in the top five.

**4. Memphis, TN — 72/100, 7.0% yield.** Memphis scores 90 on
landlord-friendliness and 89 on property-tax drag — a 0.6% effective rate,
among the lowest in the index — on a $246,954 typical value and $1,435 typical
rent. It ranks fourth rather than first because its gross-yield factor score of
71 sits nearly 20 points below Toledo's.

**5. Little Rock, AR — 72/100, 6.9% yield.** Little Rock ties Memphis at 72.3
before rounding and gets there differently: a lower entry price ($218,000, an
entry score of 87 against Memphis's 66) offsets a slightly thinner 6.9% yield
and a lower growth score of 45. It is the cheapest top-five market after
Toledo.

## The counterintuitive finding: Chicago

**Chicago posts a 7.6% gross rental yield and a price-to-rent ratio of 13 —
numbers that match the top of the table — and still scores 53, below 14 of the
15 ranked markets.** (San Antonio also displays 53; Chicago is the lower of the
two before rounding, at 52.7 against 53.2.) Its gross-yield factor score is 88,
third-highest of the 18 metros in the index, behind only Pittsburgh (94) and
Toledo (90). Everything after that goes the other way: 35 on
landlord-friendliness, the lowest score in the index; 6 on property-tax drag,
against a 2.1% effective rate; and 0 on
entry price, because a $359,897 typical home value is above the $340,000
ceiling of the entry factor. Chicago is the clearest case in the data of a
market where the headline ratio and the collectable return part company.

Chicago is not alone in the pattern. New Orleans yields 7.3% at a ratio of 14 —
a top-three gross yield — and scores 62, eleventh, held down by a climate and
insurance risk score of 25, the lowest in the index. Both are reminders that
gross yield is 35% of the Star Score, not all of it.

## Methodology

The Star Score is a 0-100 index of how well a US metro suits a buy, improve,
refinance, repeat strategy. It weights gross rental yield 35%, entry price
against a $100,000 capital base 15%, landlord-friendliness 15%, equity growth
15%, property-tax drag 10%, and climate and insurance risk 10%. Each factor is
mapped to a 0-100 subscore and the index is the weighted sum; the weights and
the factor definitions are published on the site's `/methodology` page and
implemented in `engine/scoring.py`. Gross yield is annualized typical rent
divided by typical home value, and the price-to-rent ratio is typical home
value divided by twelve months of typical rent. Fifteen metros are ranked;
Chicago, Austin and Denver are carried as reference markets to show the range of
the index rather than to recommend them.

## Data vintage

Home values are Zillow Home Value Index (ZHVI) metro figures and rents are
Zillow Observed Rent Index (ZORI) metro figures, both June 2026 — the most
recent vintage in the dataset behind this edition. Supporting context comes
from the US Census ACS, HUD Fair Market Rents, state landlord-tenant statutes
and Tax Foundation effective property-tax tables. The landlord-friendliness,
equity growth, and climate and insurance risk factors are editorial scores on
public data, reviewed September 2026; they are judgments, not measurements, and
are labeled as such on every page. Yields and ratios are gross: they are before
vacancy, maintenance, management, insurance and financing costs, all of which
are local.

This is the first quarterly edition of these rankings, so it reports no
quarter-over-quarter movement. Rank and score changes will be reported from
Q4 2026 forward, against this edition as the baseline.

## For editors

- **How to cite:** "According to Snowball Atlas's Star Score index, Toledo, Ohio
  ranks first among US rental markets in Q3 2026 with a score of 77 out of 100
  and a 7.7% gross rental yield." Please cite the index as the **Star Score**
  and Snowball Atlas as the source, with a link to the rankings page where
  possible.
- **Rankings page:** `/rentals/best-rental-markets-2026`
- **Per-metro pages carry the full data** — typical home value, typical rent,
  price-to-rent ratio, gross yield, the six factor subscores with their weights,
  and the source and review dates — at `/rentals/<metro-slug>`, for example
  `/rentals/toledo-oh` or `/rentals/chicago-il`. Every number in this report is
  reproducible from those pages.
- **Methodology and sources:** `/methodology`
- Paths above are relative to the Snowball Atlas site root; the live domain is
  set at build time via `BASE_URL`, so use the canonical URL printed on the
  page you are citing.
- **Figures in this report are as of June 2026 (Zillow ZHVI/ZORI), reviewed
  September 2026.** If you are publishing after the next quarterly refresh,
  check the rankings page for the current vintage.
- Not investment advice.
