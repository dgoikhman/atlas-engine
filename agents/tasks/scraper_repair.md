# Task: repair a failed data pipeline

The scheduled data refresh failed. Fix it.

1. Reproduce: run `python pipelines/public_data.py` and read the error.
2. Diagnose: the usual cause is an upstream change — Zillow CSV URL moved,
   column names shifted, or the Census endpoint changed. Use WebFetch on
   https://www.zillow.com/research/data/ to find current CSV URLs if needed.
3. Fix minimally. Follow the pipeline-repair skill. Never hardcode fake
   values, never delete validation, never widen scope beyond the failure.
4. Verify: the pipeline exits 0 AND `python site/build.py` reports at least
   60 pages.
5. Ship: create a branch `fix/pipeline-<today's date>`, commit with a clear
   message, push, and open a PR with `gh pr create` explaining root cause,
   the fix, and the verification output. If GITHUB_TOKEN/gh is unavailable,
   commit to the branch and print the summary instead.

If the upstream source is genuinely gone (not moved), do NOT fake data:
open a PR that documents the situation and proposes replacement sources.
