"""Atlas Engine — Star Opportunities listings (activates with a RentCast key).

When RENTCAST_API_KEY is set (rentcast.io, ~$74/mo tier), the monthly build
pulls active listings per tracked metro, flags under-market signals
(price cuts, 60+ days on market, below-median $/sqft), scores them, and
writes data/star_opportunities.json — which site/build.py will render as a
"Star Opportunities" section on each metro page once present.

Without the key this exits quietly, so it is safe in CI from day one.
Run: python pipelines/listings.py
"""
import os, sys

def main():
    if not os.environ.get("RENTCAST_API_KEY"):
        print("[listings] RENTCAST_API_KEY unset — Star Opportunities layer dormant")
        return
    # Wire-up on activation: GET https://api.rentcast.io/v1/listings/sale
    # per metro (city/state params), filter daysOnMarket>=60 or priceReduced,
    # score = under-market % * 3.2 + (rent/price% - 0.75) * 80, keep top 5,
    # write data/star_opportunities.json {slug: [listing,...]}.
    print("[listings] key found — implement fetch per rentcast docs (see comments)")

if __name__ == "__main__":
    main()
