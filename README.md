# Atlas Engine

One chassis, many atlases. Data pipelines → named scores → programmatic AEO pages.
First atlas live in this repo: **Snowball Atlas** (US rental markets, Star Score index).

## Quick start (5 minutes)
    pip install -r requirements.txt
    python site/build.py --base-url https://YOURDOMAIN.com
    # -> out/ contains 66 static pages: deploy to Cloudflare Pages or Netlify

## Refresh with live data
    python pipelines/public_data.py     # pulls latest Zillow ZHVI/ZORI + Census
    python site/build.py --base-url https://YOURDOMAIN.com

## Franchise Atlas pipeline
    export ANTHROPIC_API_KEY=sk-...
    python pipelines/fdd.py fetch --query "coffee" --limit 20   # MN CARDS
    python pipelines/fdd.py extract "data/raw/fdd/*.pdf"        # Claude Batch API
    python pipelines/fdd.py poll <batch_id>                     # -> data/fdd_extracted/

## Deploy checklist (your ~20 minutes)
1. Push this repo to GitHub.
2. Cloudflare Pages → connect repo → build command `python site/build.py --base-url https://YOURDOMAIN.com` (or commit out/ and serve it directly).
3. Point the domain; submit sitemap.xml to Google Search Console AND Bing Webmaster Tools (Bing feeds ChatGPT).
4. Free Census key (optional): api.census.gov · HUD token (optional): huduser.gov
5. Cron the refresh: monthly `public_data.py` + `build.py` (GitHub Actions works).

## Repo map
    data/seed_metros.csv     18 metros, real June 2026 Zillow figures (via Lofty)
    data/metros_live.csv     written by pipelines; build.py prefers it when present
    db/schema.sql            Postgres schema for when CSV outgrows itself
    engine/scoring.py        named-index framework; add a config per new atlas
    pipelines/public_data.py Zillow + Census + HUD (free, no scraping)
    pipelines/fdd.py         MN CARDS fetch + Claude Haiku batch extraction
    site/build.py            the page factory: metro/rankings/comparison pages,
                             FAQ+Dataset JSON-LD, sitemap, robots, llms.txt

## Next milestones (from the launch plan)
- Zip-level pages behind Pro tier (Zillow publishes zip CSVs — same pipeline)
- Email capture + alerts (alert_sub table is ready in schema.sql)
- Franchise Atlas pages from fdd_extracted/ (new template pair in build.py)
- STR Atlas via Inside Airbnb ingestion

## Automation
See SETUP.md — one push + two settings and the site deploys itself monthly,
repairs its own pipelines by PR, and drafts quarterly reports. Agents run on
the Claude Agent SDK with skills in .claude/skills/.
