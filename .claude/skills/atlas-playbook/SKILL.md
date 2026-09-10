---
name: atlas-playbook
description: Core conventions for the Atlas Engine repo — repo map, data provenance rules, AEO page requirements, scoring framework. Consult before changing pipelines, templates, scores, or writing any content.
---

# Atlas Engine playbook

## Repo map
- data/seed_metros.csv — baseline metro data; data/metros_live.csv — pipeline output (build prefers it)
- pipelines/public_data.py — Zillow/Census/HUD refresh; pipelines/fdd.py — FDD fetch + Claude Batch extraction
- engine/scoring.py — named-index framework (Star Score config); add a config block per new atlas
- site/build.py — page factory; renders all pages + sitemap + robots + llms.txt to out/
- agents/ — autonomous task prompts + runner; .github/workflows/ — schedules

## Non-negotiables
1. Data provenance: every number on a page traces to a named source and date. Never fabricate, estimate, or "refresh from memory". If data is missing, the page says so or isn't built.
2. ToS discipline: government/open data and licensed APIs only. Never add scraping of Zillow listings, BizBuySell, or other ToS-protected marketplaces.
3. Truthful dates: last-reviewed dates update only when data or review actually happened.

## AEO page requirements (every page)
- First paragraph contains one citable sentence: number + geo + date.
- Data in tables, not prose. FAQPage + Dataset JSON-LD where applicable.
- Server-rendered static HTML only; nothing meaningful behind JS.
- Internal links: metro -> comparisons -> rankings -> methodology.
- After template changes, verify: python site/build.py exits 0 and page count >= 60.

## Scoring
Star Score = weighted factors in engine/scoring.py (yield .35, entry .15, landlord .15, growth .15, tax .10, climate .10). Weight changes are a product decision — propose in a PR description, never change silently.

## Commands
- Refresh: python pipelines/public_data.py
- Build: python site/build.py --base-url <domain>
- Agents: python agents/run_agent.py <scraper_repair|fdd_qa|report_writer>
