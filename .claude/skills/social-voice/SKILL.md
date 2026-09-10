---
name: social-voice
description: Voice, platform rules, and approval flow for Atlas social content (X and Reddit). Consult before drafting any social post, thread, or community reply.
---

# Atlas social voice

## Voice
- Numbers first. Every post carries at least one specific stat with geo + date.
- Plain and confident. No hype adjectives, no rocket emojis, no "game-changer".
- One idea per post. Rankings get a short thread, not a wall.
- Charts beat text: when a post cites 3+ numbers, note "attach chart: <which>".

## X mechanics
- Main posts: standalone insight, NO link. (Two reasons: link posts cost
  $0.20 each on the pay-per-use API vs $0.015 plain, and links reduce reach.)
  When a link matters, write "link in reply" and put the URL in a reply the
  human can add, or reference the site name in text.
- Cadence: 3-5 posts/week. Formats that work: leaderboard change, one-metro
  spotlight stat, counterintuitive finding, this-vs-that comparison.
- Never engage in dunks, politics, or replies beyond factual clarification.

## Reddit — HARD RULES
- Agents NEVER post to Reddit. Drafts only; a human posts manually.
  (Subreddit rules + Reddit's platform norms: undisclosed automation and
  self-promotion get accounts banned and domains blacklisted — the exact
  asset we're building would be the casualty.)
- Every draft targets a specific subreddit and answers a real recurring
  question in that community, natively — the value must survive with the
  link removed.
- Disclose affiliation plainly ("I built this dataset/site") when the site
  comes up. 90/10 rule: 9 pure-value contributions per 1 that mentions us.
- Respect each sub's self-promotion rules; when in doubt, the draft says
  "check sub rules before posting".

## Approval flow (non-negotiable)
Drafts land as files in content/social/queue/ via PR. NOTHING posts until a
human merges the PR. The daily poster only publishes merged, due, X-platform
items. Reddit files are never auto-posted regardless of merge status.
