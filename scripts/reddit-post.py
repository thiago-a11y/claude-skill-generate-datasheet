#!/usr/bin/env python3
"""
Post launch announcement to multiple subreddits via Reddit API.

Setup:
  1. Create Reddit app at https://www.reddit.com/prefs/apps/ (type: script)
  2. Copy scripts/.env.example to scripts/.env and fill credentials
  3. pip install praw python-dotenv
  4. python scripts/reddit-post.py [--dry-run] [--sub SUBREDDIT]

Usage:
  python scripts/reddit-post.py --dry-run          # Preview without posting
  python scripts/reddit-post.py --sub ClaudeAI      # Post to one subreddit
  python scripts/reddit-post.py                     # Post to all subreddits (with delays)
"""

import argparse
import os
import sys
import time
from pathlib import Path

try:
    import praw
    from dotenv import load_dotenv
except ImportError:
    print("Install dependencies: pip install praw python-dotenv")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
POST_FILE = PROJECT_ROOT / "skills" / "generate-datasheet" / "launch-post-reddit.md"

SUBREDDITS = [
    {"name": "ClaudeAI",      "flair": "Show & Tell",   "note": "Primary audience — Claude Code users"},
    {"name": "ClaudeDev",     "flair": None,             "note": "Claude developer community"},
    {"name": "ChatGPTCoding", "flair": None,             "note": "AI coding tools audience"},
    {"name": "SideProject",   "flair": None,             "note": "Indie builders, side projects"},
    {"name": "opensource",    "flair": None,             "note": "Open source community"},
    {"name": "programming",   "flair": None,             "note": "Large — check rules before posting"},
    {"name": "webdev",        "flair": None,             "note": "Web developers"},
    {"name": "devops",        "flair": None,             "note": "Ops angle: runbooks, health score, bus-factor"},
]

DELAY_BETWEEN_POSTS = 600  # 10 min — Reddit rate limits


def load_post():
    content = POST_FILE.read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    title = lines[0].lstrip("# ").strip()
    body = "\n".join(lines[1:]).strip()

    return title, body


def create_reddit():
    load_dotenv(SCRIPT_DIR / ".env")

    required = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        print(f"Copy scripts/.env.example to scripts/.env and fill credentials")
        sys.exit(1)

    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="claude-skill-generate-datasheet-launch/1.0",
    )


def post_to_subreddit(reddit, sub_config, title, body, dry_run=False):
    name = sub_config["name"]
    flair = sub_config["flair"]

    if dry_run:
        print(f"  [DRY RUN] r/{name} — would post with title ({len(title)} chars)")
        if flair:
            print(f"            flair: {flair}")
        return True

    try:
        subreddit = reddit.subreddit(name)

        kwargs = {"title": title, "selftext": body}

        if flair:
            flair_choices = list(subreddit.flair.link_templates)
            match = next((f for f in flair_choices if f["text"] == flair), None)
            if match:
                kwargs["flair_id"] = match["id"]
            else:
                print(f"  [WARN] Flair '{flair}' not found in r/{name}, posting without flair")

        submission = subreddit.submit(**kwargs)
        print(f"  [OK] r/{name} — {submission.url}")
        return True

    except praw.exceptions.RedditAPIException as e:
        print(f"  [FAIL] r/{name} — {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] r/{name} — {type(e).__name__}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Post to Reddit subreddits")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--sub", type=str, help="Post to a single subreddit only")
    parser.add_argument("--no-delay", action="store_true", help="Skip delay between posts")
    parser.add_argument("--list", action="store_true", help="List target subreddits and exit")
    args = parser.parse_args()

    if args.list:
        print("Target subreddits:\n")
        for s in SUBREDDITS:
            flair_str = f" (flair: {s['flair']})" if s["flair"] else ""
            print(f"  r/{s['name']}{flair_str} — {s['note']}")
        return

    title, body = load_post()
    print(f"Post: {title[:80]}...")
    print(f"Body: {len(body)} chars\n")

    targets = SUBREDDITS
    if args.sub:
        targets = [s for s in SUBREDDITS if s["name"].lower() == args.sub.lower()]
        if not targets:
            targets = [{"name": args.sub, "flair": None, "note": "custom"}]

    reddit = None if args.dry_run else create_reddit()

    results = {"ok": 0, "fail": 0}
    delay = 0 if (args.dry_run or args.no_delay) else DELAY_BETWEEN_POSTS

    for i, sub in enumerate(targets):
        if i > 0 and delay > 0:
            print(f"\n  Waiting {delay}s (Reddit rate limit)...")
            time.sleep(delay)

        success = post_to_subreddit(reddit, sub, title, body, dry_run=args.dry_run)
        results["ok" if success else "fail"] += 1

    print(f"\nDone: {results['ok']} posted, {results['fail']} failed")


if __name__ == "__main__":
    main()
