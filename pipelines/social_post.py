"""Atlas Engine — X poster.

Publishes APPROVED (merged), DUE (date <= today), X-platform items from
content/social/queue/ and moves them to content/social/posted/.
Reddit files are always skipped: humans post those by hand (see the
social-voice skill for why).

Auth (X pay-per-use API, OAuth 1.0a user context) via env vars:
  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET
Missing credentials -> exits quietly (lets CI run before X is set up).
Cost note: plain posts bill ~$0.015 each; posts containing URLs ~$0.20 —
the voice skill says keep links out of main posts anyway.
"""
import os, sys, glob, datetime, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "content", "social", "queue")
POSTED = os.path.join(ROOT, "content", "social", "posted")


def parse(path):
    text = open(path).read()
    meta, body = {}, text
    if text.startswith("---"):
        try:
            head, body = text.split("---", 2)[1:]
            for line in head.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.split("#")[0].strip()
        except ValueError:
            pass
    return meta, body.strip()


def main():
    keys = [os.environ.get(k) for k in
            ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")]
    if not all(keys):
        print("[social] X credentials not set — nothing posted")
        return
    from requests_oauthlib import OAuth1Session
    x = OAuth1Session(keys[0], keys[1], keys[2], keys[3])
    today = datetime.date.today().isoformat()
    os.makedirs(POSTED, exist_ok=True)
    posted = 0
    for path in sorted(glob.glob(os.path.join(QUEUE, "*.md"))):
        meta, body = parse(path)
        if meta.get("platform", "").lower() != "x":
            continue  # reddit and anything else: human-posted only
        if meta.get("date", "9999") > today:
            continue  # not due yet
        if not body or len(body) > 280:
            print(f"[social] SKIP {os.path.basename(path)}: empty or >280 chars")
            continue
        r = x.post("https://api.twitter.com/2/tweets", json={"text": body})
        if r.status_code in (200, 201):
            shutil.move(path, os.path.join(POSTED, os.path.basename(path)))
            posted += 1
            print(f"[social] posted {os.path.basename(path)}")
        else:
            print(f"[social] FAILED {os.path.basename(path)}: "
                  f"{r.status_code} {r.text[:200]}")
    print(f"[social] done — {posted} posted")


if __name__ == "__main__":
    main()
