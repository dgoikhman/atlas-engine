# Method & provenance — influencers-rentals-brrrr.csv

Scouted 2026-09-10 for the `rentals-brrrr` vertical (no `NEXT_VERTICAL.txt` present,
so the default applied). 28 rows, ranked; **row order is the ranking** because
`agents/tasks/outreach_writer.md` consumes "the top 10 rows" positionally.

## Ranking basis

Rank = **verified reach × topical fit × route quality**, not reach alone.

"Topical fit" means: does this audience make US metro-level *rental* buy/hold
decisions, i.e. the variables Star Score actually scores (yield, entry cost,
landlord friction, growth, tax, climate)? "Route quality" means: is there a
public business intake we can legitimately use?

Two consequences worth knowing before reading the file:

- **The largest audience is not rank 1.** Investment Joy (2.52M) sits at rank 14
  because rentals are one slice of a general small-business channel.
- **Two unverified-size rows rank top 5** (Jay Parsons #4). They are ranked on
  fit and on having a confirmed paid-sponsor program; their size must be
  established in the first conversation before any spend.

## Audience numbers are NOT comparable across rows

Each `audience_estimate` is a verbatim visible string plus its source and date.
But the *kind* of number differs by platform, and mixing them would be
misleading:

| Kind | Rows | Caveat |
|---|---|---|
| YouTube subscribers | Carson, Zuber, McElroy, Kwak, Smith, Investment Joy, Rookie, Reventure, Dion | Rounded by YouTube itself ("1.27M"). Not exact integers. |
| Newsletter list size | Zero Flux, CRE Daily, Best Ever, STR Scout, Lohmann | Self-reported on own landing/advertise pages; not audited. |
| Apple Podcasts ratings count | On The Market, Rental Income, Real Estate Guys, Rookie | **A ratings count, not audience size.** Does not track download rank — On The Market's 864 ratings vs Get Rich Education's millions of downloads are not on the same scale. |
| Cumulative downloads | Get Rich Education | Lifetime total, not monthly. Only IAB-certified figure in the file. |
| Discord API member count | Real Estate Investors United | The one precisely verified live count here. |
| Third-party tracker | Kathy Fettke | Weakest sourcing in the file. Re-verify before use. |

## Verification failures (do not paper over these)

- **Reddit is entirely unverifiable from this environment.** WebFetch, WebSearch
  with `allowed_domains`, direct curl on every subdomain, `r.jina.ai`, Redlib
  mirrors and CORS proxies all returned 403 or a verification wall. Reddit blocks
  our user agent by policy. **No subreddit member count is recorded.** The two
  Reddit rows carry routes and rules only; a human must confirm size in a browser.
  We also could **not** confirm `r/BRRRR` exists — do not assume it does.
- **Facebook Groups: no verifiable number for any group.** Group pages are
  login-walled. Counts circulating in listicles (leadhall.com et al.) could not
  be confirmed and the listicle itself reads as generated content. No FB row was
  written rather than laundering those numbers.
- **x.com returns HTTP 402** to our fetcher; Instagram is login-walled; Social
  Blade / HypeAuditor / NoxInfluencer / ViewStats are 403 or JS-gated. X follower
  counts for Lambert, Palacios, Mohtashami and Meyer are unverified. Where a
  number appears for these people it came from their own site or from
  threads.com, which renders counts without a login.
- **YouTube counts required a direct page fetch, not WebFetch.** `youtube.com`
  renders the subscriber count client-side, so WebFetch sees only footer
  boilerplate. Counts were extracted from the server-delivered
  `contentMetadataViewModel` header block, anchored on each channel's canonical
  `@handle`. **A re-checker using WebFetch will see nothing and may wrongly
  conclude these were fabricated.** Re-run the extractor, don't WebFetch.
- **403 on fetch, so excluded:** John Burns Research (a "40,000+ subscribers"
  figure is attributed to their /subscribe page by search snippets but the domain
  403s us) and CalculatedRisk (near-perfect format fit; a third-party "40k
  readers" figure exists but no first-party confirmation).

## Numbers that circulate but must NOT be used

- **BiggerPockets "600,000 email subscribers"** — not on the live page; traces to
  a now-404 `/advertise.html`. Do not cite.
- **BiggerPockets self-contradicts**: `/advertise` says "+2 million members",
  `/about` says "over 3,000,000". Always cite the specific page.
- **BiggerPockets "$5,000 podcast ad minimum"** — search snippet only, unverified.
- **The Real Estate Guys "17 million downloads / 250,000 listens per month"** —
  search snippet only; absent from both pages fetched.
- **Coach Carson's "132,000 subscribers"** string is attached to a *YouTube*
  module on his site, not his email list. His list is separately labelled "42K".
- **DealMachine "150,000+"** and **Stessa "350,000+"** are *software user* counts,
  not newsletter lists — no DealMachine row was written on a list-size basis.
- **ResiClub "Nears 1 Million Monthly Readers"** is a monthly-readers metric from
  an unfetchable LinkedIn post, not list size.

## Contact-path discipline

Public business routes only. **No personal email address is recorded in the CSV**,
including ones publicly displayed on Chandler David Smith's site, in Dion
McNeeley's channel description, and behind ResiClub's and Zero Flux's "Advertise"
links (both resolve to personal mailtos, which is why those rows say
"DM (draft for human send)" instead).

Three rows are DM-only: ResiClub, Zero Flux, STR Scout.

## Where our offer is not permitted

Verified from rules text — a link post or data drop would be removed:

- **BiggerPockets forums** — promotion is Classifieds-only (2 threads/day, 5-day
  repeat gap). Rule O: "No form of affiliate marketing is allowed." So the BP row
  is `partnership` via the ad desk, never `affiliate`.
- **r/RealEstate** — explicit "no self-promotion / no website links" plus
  aggressive automod. Listed in the row-28 note as do-not-pitch.
- **City-Data** and **Mr. Money Mustache forum** — both define linking your own
  content as spam; MMM allows in-context links inside existing threads only.
  Neither earned a row.

Sanctioned commercial routes that *do* exist: BiggerPockets `/advertise`,
National REIA Industry Partners (vendor registration), MrLandlord "Partner With
Us", and the rate-carded newsletter programs (CRE Daily, Peter Lohmann, Best Ever
CRE, Jay Parsons).

Per `.claude/skills/social-voice/SKILL.md`, agents never post to Reddit —
these are drafts, a human sends, and nothing publishes without a merged PR.

## Known gap

No strong 2025–2026 *riser* surfaced; searches returned institutional dashboards
(HomeStats, FHFA) rather than individual creators. The highest-yield next pass
would be the ResiDay 2026 speaker list and the #REtwit operator orbit, which
needs X access we don't have.
