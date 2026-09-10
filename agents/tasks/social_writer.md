# Task: draft the week's social content

Produce this week's queue of X posts and Reddit drafts. Follow the
social-voice skill exactly.

1. Run `python site/build.py` and read the rankings output for current
   scores/yields/values. Check `git log --oneline -20` and recent diffs to
   data/ for anything that CHANGED (rank moves, new data month) — changes
   are the best content. Use only real numbers from the build output.
2. Write 4-5 X post files and 1-2 Reddit draft files into
   content/social/queue/, named YYYY-MM-DD-slug.md, each with this header:

   ---
   platform: x            # or: reddit
   date: 2026-09-14       # earliest posting date
   subreddit: r/realestateinvesting   # reddit only
   chart: rankings-top5   # optional note for the human
   ---
   Post text here.

3. Spread X dates across the coming week. Reddit drafts must include a
   first line comment: "HUMAN POSTS THIS — check sub rules first".
4. Open a PR on branch `content/social-<today>` titled "Social queue: week
   of <date>". In the PR body, list each post's hook in one line so review
   takes 60 seconds. Do not modify anything outside content/social/.
