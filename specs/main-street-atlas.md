# Main Street Atlas — build spec v1
*The succession-wave map. Working doc for Dan + agents. Sept 2026.*

## Thesis
Two layers. The differentiated one is NOT listings.

**Layer 1 — the Succession Radar (the moat).** Score every operating
main-street business on succession-likelihood signals — whether or not it is
listed for sale anywhere. Buyers pay for tomorrow's inventory, not
yesterday's listings. Nobody sells this map.

**Layer 2 — listed deals, bootstrapped legally.** Curated inventory from
independent brokers via partnership + a free submission portal. Brokers feed
us because we are free distribution. This layer is the SEO surface
("businesses for sale in {city}"); the Radar is the Pro product behind it.

## Legal guardrails (non-negotiable, mirror of atlas-playbook rules)
1. NEVER scrape or cache CoStar properties (LoopNet, BizBuySell, BizQuest),
   Crexi, or any ToS-protected marketplace. Not once, not "for testing."
2. Foundation = public records: state Secretary-of-State bulk data
   (FL Sunbiz bulk files, TX weekly files, CO/WA open datasets, OH).
   Filing dates, status, entity type are public facts.
3. Google Places: ToS-compliant use only — store place_ids and refresh;
   do not warehouse their content. Prefer first-party signals we compute
   ourselves (crawling the business's OWN website from registry/domain data
   is ours: site exists? copyright year stale? SSL dead?).
4. Listings appear only with documented permission (broker agreement or
   direct submission). Provenance recorded per listing.
5. Revenue is always a MODELED BAND with visible methodology (industry
   revenue-per-employee benchmarks × headcount proxies) — never presented
   as actual financials.
6. Scores describe business-level data signals, never a person's intent:
   "high succession-signal score," not "this owner wants out." No owner
   personal names on free public pages. Registered-agent/residential
   addresses suppressed.
7. Claim & correction flow on every business page ("Is this your
   business?"): verify → update or remove. Good law, good manners — and
   see Monetization: a claiming owner is a sell-side lead.

## Succession Score (engine/scoring.py → MAINSTREET config)
Named index: **Succession Score**, 0-100.
- entity_age (30%): years since registration; 20+ yrs = top band
- industry_wave (20%): silver-tsunami industries list (HVAC, plumbing,
  laundromats, machine shops, distributors, practices, landscaping…)
- digital_decay (20%): no site / stale site / dormant profile, first-party
  crawl signals
- owner_age_context (15%): Census Annual Business Survey — owner age by
  county × industry (public API; sourced, not guessed)
- demand_density (15%): buyers-per-target proxy — metro business density
  (Census CBP) vs population/income growth
Business industry classification from entity names via Haiku batch
(cheap, JSON schema, confidence field; low-confidence → excluded from
public pages, queued for review). Sanity rules per data-quality skill.

## Pages (chassis page factory, /businesses/ section)
- /businesses/{city-state}/ — "Businesses for sale & succession outlook in
  {city}": citable stat first ("X registered businesses over 20 years old;
  succession index Y"), industry mix, curated listed deals (partnered),
  anonymized sample radar rows, FAQ + JSON-LD.
- /businesses/{city-state}/{industry}/ — "laundromats in Memphis" etc.
- /businesses/succession-index/ — national rankings (the PR asset).
- Quiz fork (/start/ pattern): budget, SBA status ("financing lined up?"),
  industry experience, operator vs passive → routes to SBA lender intro,
  QoE/diligence intro, buy-side advisor, or Franchise Atlas cross-sell.

## Monetization
- Pro annual ~$490 (ETA/searchfund WTP >> REI): the Radar, filters,
  exports, "new 85+ scores in your metro" alerts.
- Broker tier: listing distribution + routed buyer leads.
- Referrals (the fat layer): SBA lenders ($1-2K/funded), QoE firms,
  M&A attorneys, valuation providers.
- Claim flow → "thinking of selling? free valuation intro" → sell-side
  broker referral. The opt-out IS a lead channel.

## Build phases
- P1 (SHIPPED as v0.1): Colorado registry via open-data API — city-level aggregates + Succession Index pages. Swapped ahead of Florida: same public-records legality, clean queryable API vs gigabyte fixed-width SFTP files. Florida moves to the scale phase. → entity age + status; MAINSTREET score
  config; 50 city pages + national index page. (FL alone ≈ 3M entities.)
- P2: name→industry Haiku classifier; first-party digital-decay crawler;
  Census ABS owner-age + CBP density joins.
- P3: broker submission portal + claim/correction flow (form endpoint),
  listed-deals rendering with provenance.
- P4: TX/CO/WA/OH states; alerts; Pro gating via membership layer.

Prereq before P1 ships publicly: membership layer live on Snowball
(shared auth = one account across atlases, per launch plan).
