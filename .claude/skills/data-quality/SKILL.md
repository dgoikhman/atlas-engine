---
name: data-quality
description: Sanity ranges and QA rules for extracted data (FDD items, metro metrics). Use when validating, reviewing flagged extractions, or adding new extraction fields.
---

# Data quality rules

## FDD sanity ranges
- item5 initial fee: $0–$500K. item7 total investment: $5K–$50M, low <= high.
- item20 units: 0–60,000 total; franchised + company ~= total (tolerance 5%).
- royalty: 0–15% typical (flag >15%, don't reject). term: 1–50 years.
- fdd_year within last 3 years for "current" datasets.

## Metro metric ranges
- home_value $50K–$2M; rent $400–$6,000/mo; ratio 5–45; tax_rate 0.2–3.0%.
- Month-over-month moves >15% are suspect — flag, compare against raw file.

## The prime directive
When a value fails a range or isn't clearly supported by the source document, FLAG for human review — never guess, interpolate, or "correct" toward plausibility. A missing number is recoverable; a confident wrong number published on a citable page is not.
