# Atlas Engine

Data-map business chassis. Pipelines pull public data, engine/scoring.py
computes named indexes (Star Score), site/build.py renders the programmatic
AEO site to out/, agents/ + .github/workflows automate the rest.

Read .claude/skills/atlas-playbook/SKILL.md before changing anything —
it holds the repo map, data-provenance rules, and AEO page requirements.

Quick commands:
- python pipelines/public_data.py       # refresh Zillow/Census data
- python site/build.py --base-url X     # build all pages to out/
- python agents/run_agent.py <task>     # scraper_repair | fdd_qa | report_writer

House rules: no fabricated data, no ToS-violating scrapers, truthful
last-reviewed dates, citable stat in every first paragraph.
