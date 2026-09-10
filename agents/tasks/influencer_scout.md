# Task: scout influencers & communities for a vertical

Vertical for this run: read content/growth/NEXT_VERTICAL.txt if present,
else default to "rentals-brrrr".

1. Via WebSearch, identify the ~25 most relevant creators, podcasts,
   newsletters and communities for the vertical (BRRRR/REI: BiggerPockets
   orbit, REI YouTube/Twitter; boring-business: Contrarian Thinking, SMB
   Twitter/ETA, Acquisitions Anonymous, Searchfunder, deal newsletters;
   franchise: franchise YouTube reviewers, r/franchising, broker networks).
2. Write content/growth/influencers-<vertical>.csv with columns:
   name, platform, audience_estimate, focus, contact_path, best_offer,
   evidence_url, note
   - best_offer ∈ data-drop | affiliate | guest-pitch | embed | partnership
   - contact_path: PUBLIC business contact pages/forms only. Never scrape
     personal emails; "DM (draft for human send)" is a valid path.
   - audience_estimate must come from a visible public number; cite the url.
3. Rank by (audience × fit). Flag the single best anchor-partner candidate.
4. Open a PR on branch growth/scout-<vertical>-<date> summarizing the top
   10 in the PR body, one line each.
