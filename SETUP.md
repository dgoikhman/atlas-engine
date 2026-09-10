# Go-live checklist (~20 minutes, once)

## 1. Push the repo
    git init && git add -A && git commit -m "atlas engine v0.1"
    gh repo create atlas-engine --private --source . --push
(or create the repo on github.com and `git push` to it)

## 2. Turn on the website (free, no other accounts)
GitHub repo -> Settings -> Pages -> Source: **GitHub Actions**.
Then Actions tab -> "Refresh data and deploy site" -> Run workflow.
Site goes live at https://<you>.github.io/atlas-engine/ within ~2 minutes.

## 3. Add the two settings
- Settings -> Secrets and variables -> Actions -> **Secrets** -> New:
  `ANTHROPIC_API_KEY` = your key from platform.claude.com
- Same page -> **Variables** -> New:
  `BASE_URL` = your real domain once you buy it (e.g. https://snowballatlas.com)

## 4. Custom domain (when you've bought it)
Settings -> Pages -> Custom domain -> enter it, add the DNS records GitHub
shows you, re-run the deploy workflow so canonicals/sitemap use BASE_URL.
Then submit https://YOURDOMAIN/sitemap.xml to Google Search Console AND
Bing Webmaster Tools (Bing feeds ChatGPT).

## 5. Daily driver
Install Claude Code (claude.com/code), open this repo, and delegate:
it reads CLAUDE.md and .claude/skills/ automatically. Same brain that
runs unattended in the workflows above.

## What now runs by itself
- Monthly: Zillow/Census refresh -> rebuild -> deploy. If the refresh
  breaks, the scraper-repair agent is triggered automatically and opens a
  PR with the fix for you to approve.
- Quarterly: the report-writer agent drafts the citable Star Score
  rankings report as a PR (your data-PR flywheel).
- On demand: Actions -> "Run agent task" -> fdd_qa after each FDD
  extraction batch.

## Cost guardrails already in place
Agents run with max_turns=60 and 30-minute CI timeouts; extraction uses
the Batch API (50% cheaper); the monthly refresh itself uses zero AI.
Expected idle-month spend: cents to a few dollars.

## Optional upgrades (later)
- Cloudflare Pages instead of GitHub Pages (faster edge, same out/ dir)
- HUD_TOKEN / CENSUS_KEY secrets for the extra data sources
- Managed Agents (platform.claude.com/docs/en/managed-agents/overview)
  for long-running jobs beyond CI's 30-minute comfort zone

## Social layer (optional, add when ready)
X posting uses X's pay-per-use API (~$0.015/plain post; keep links out of
main posts — URL posts bill ~$0.20 and travel worse anyway):
1. developer.x.com -> create app on the Snowball Atlas account -> generate
   OAuth 1.0a user tokens (read+write).
2. Add repo secrets: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET.
3. Flow: Monday agent PR ("Social queue: week of ...") -> you review/edit ->
   merge = approve -> daily job posts due items. ~$5-15/mo at 3-5 posts/week.
Reddit: the agent drafts into the same PR but NOTHING auto-posts to Reddit —
you post those by hand from the drafts. That's a rule, not a limitation.
