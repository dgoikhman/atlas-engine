# Task: write the quarterly Star Score rankings report

Produce the data-PR flagship: a press-ready report journalists can cite.

1. Run `python site/build.py` and read the generated rankings page under
   `out/rentals/` to get current scores, yields, values and rents. Use ONLY
   these numbers — never invent or "update" figures from memory.
2. Write `content/reports/star-score-rankings-<year>-Q<quarter>.md`:
   - Headline finding in the first sentence, with numbers (citable).
   - Top 5 markets with one short paragraph each: score, yield, what drives it.
   - One counterintuitive finding (e.g. a high-ratio market scoring low, or
     a mover) — this is what gets quoted.
   - A methodology paragraph and data-vintage note, per the atlas playbook.
   - Tone: confident, plain, numbers-forward. No hype adjectives.
3. Include a "for editors" footer: how to cite ("According to Snowball
   Atlas's Star Score index..."), and that per-metro pages carry full data.
4. Commit on branch `content/rankings-<year>-Q<quarter>` and open a PR.
