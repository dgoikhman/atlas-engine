# Task: research sourced market context (top employers, institutions, highlights)

Enrich the top metros with REAL, source-verified local context. This is the
layer that must never be generated from memory — every claim needs a live
web source found via WebSearch.

1. Read data/metros_live.csv; take the 25 highest Star Score metros (compute
   with engine/scoring.py or approximate by yield) that do NOT already have
   a file in content/context/.
2. For each (limit this run to 5 metros to stay reviewable): research via
   WebSearch and write content/context/<slug>.json:
   {"slug": "...", "employers": [{"name": "...", "note": "sector / approx headcount", "source": "url"}],
    "institutions": ["university / hospital / base — one line each"],
    "highlights": ["2-4 genuinely notable things to see or neighborhoods to know, each verifiable"],
    "sources": ["urls used"], "researched": "YYYY-MM-DD"}
3. Rules: 3-6 employers max, only ones you can source; no restaurant lists
   (they go stale — name districts, not businesses); every entry traceable
   to a source URL; if sourcing is thin for a metro, skip it and say so.
4. Open a PR on branch content/context-<date> listing which metros were
   researched and which were skipped. The site renders these files into the
   /living/ pages once merged (template slot ships separately).
