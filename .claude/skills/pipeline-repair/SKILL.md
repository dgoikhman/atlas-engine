---
name: pipeline-repair
description: Runbook for diagnosing and fixing broken data pipelines (Zillow, Census, CARDS). Use whenever a pipeline errors, returns zero rows, or CI refresh fails.
---

# Pipeline repair runbook

1. Reproduce first. Run the failing pipeline; read the full traceback. Never fix blind.
2. Classify the failure:
   - HTTP 404/redirect -> source URL moved. WebFetch the source's index page (e.g. zillow.com/research/data/) to find the new URL.
   - KeyError/empty match -> columns or HTML changed. Download and inspect the actual payload in data/raw/ before editing parsers.
   - HTTP 403/429 -> add polite backoff and honest User-Agent; if it persists the source may disallow automation — stop and report, do not evade.
3. Fix minimally: smallest diff that restores correctness. Keep validation intact.
4. Verify: pipeline exits 0, row counts within 20% of previous run (check data/ diffs), site build succeeds with >= 60 pages.
5. Never: hardcode data values, silence exceptions broadly, delete sanity checks, or expand scope. A pipeline that fails loudly beats one that lies.
