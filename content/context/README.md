# content/context/

Hand-researched, source-verified local market context, one JSON file per metro
slug. These files are the *only* place in the repo where narrative local claims
live, and they exist precisely because such claims must never be generated from
model memory.

The `/living/` pages render these once the template slot ships.

## Schema

```json
{
  "slug": "florence-sc",
  "employers": [
    {"name": "...", "note": "sector / approx headcount", "source": "https://..."}
  ],
  "institutions": ["university / hospital / base — one line each"],
  "highlights": ["2-4 notable places or districts to know, each verifiable"],
  "sources": ["every url used"],
  "researched": "YYYY-MM-DD"
}
```

`slug` must match a slug in `data/metros_live.csv`.

## Rules

1. **Every claim traces to a live URL that was actually fetched.** Not recalled,
   not inferred from a company's general reputation. If the page didn't load,
   the claim doesn't ship.
2. **3-6 employers**, each with its own `source`. Prefer the employer's own site,
   a chamber/economic-development major-employer list, or a federal dataset
   (NCES, BLS, Census) over aggregators like Zippia, ZoomInfo or Glassdoor.
3. **Date any figure that isn't current-year.** Headcounts drift; a note reading
   "6,700+ team members (October 2024)" stays true, "6,700 employees" rots.
4. **Omit rather than estimate.** If published headcounts disagree across
   sources and no primary confirms one, give the sector and say the number is
   unconfirmed. See `mobile-al.json` for the pattern.
5. **Scope claims to the metro.** A system-wide headcount for a multi-county
   hospital network is not a metro employment figure — label it as system-wide.
   Watch for plants in adjacent counties outside the MSA.
6. **No restaurant or individual-business lists in `highlights`.** They go stale
   within a year. Name districts, parks, museums, and institutions instead.
7. **Skip thin metros.** A metro with no sourceable employer list is better left
   without a file than filled with plausible-sounding guesses. Note the skip in
   the PR description.

## Re-review

`researched` is a truthful date: bump it only when someone actually re-opened
the sources and checked them. Headcount and award claims are the first things
to rot — re-verify roughly annually.
