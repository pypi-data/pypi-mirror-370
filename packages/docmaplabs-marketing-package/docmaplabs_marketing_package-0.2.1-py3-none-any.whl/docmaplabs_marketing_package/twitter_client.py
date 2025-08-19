import time
import requests
from typing import List, Dict, Any, Optional
from .config import settings


def _auth_headers() -> Dict[str, str]:
    # Prefer OAuth2 Bearer if provided via env (not currently modeled); fallback is OAuth1 user context not implemented in this OSS client.
    # For simplicity, accept preconfigured bearer token via env TWITTER_BEARER_TOKEN
    token = None
    try:
        import os
        token = os.getenv("TWITTER_BEARER_TOKEN")
    except Exception:
        token = None
    if not token:
        raise RuntimeError("TWITTER_BEARER_TOKEN not set; please provide a bearer token or implement OAuth1.")
    return {"Authorization": f"Bearer {token}"}


def search_recent(query: str, since_id: Optional[str] = None, max_results: int = 20) -> Dict[str, Any]:
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": str(max_results),
        "tweet.fields": "id,text,author_id,created_at,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name,public_metrics",
    }
    if since_id:
        params["since_id"] = since_id
    resp = requests.get(url, headers=_auth_headers(), params=params, timeout=15)
    if resp.status_code == 429:
        # Surface rate limit with reset if available
        reset = resp.headers.get("x-rate-limit-reset")
        raise RuntimeError(f"RATE_LIMIT:{reset}")
    resp.raise_for_status()
    return resp.json()


def normalize_tweets(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    users = {u.get("id"): u for u in (payload.get("includes", {}).get("users", []) or [])}
    out = []
    for tw in payload.get("data", []) or []:
        u = users.get(tw.get("author_id")) or {}
        out.append({
            "id": tw.get("id"),
            "author": f"@{u.get('username')}" if u.get("username") else None,
            "text": tw.get("text"),
            "createdAt": tw.get("created_at"),
            "metrics": tw.get("public_metrics") or {},
        })
    return out


def search_recent_with_backoff(query: str, since_id: Optional[str] = None, max_results: int = 20, max_retries: int = 3) -> Dict[str, Any]:
    """Search with automatic 429 backoff using x-rate-limit-reset or exponential fallback."""
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": str(max_results),
        "tweet.fields": "id,text,author_id,created_at,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name,public_metrics",
    }
    if since_id:
        params["since_id"] = since_id
    attempt = 0
    while True:
        resp = requests.get(url, headers=_auth_headers(), params=params, timeout=15)
        if resp.status_code == 429:
            reset = resp.headers.get("x-rate-limit-reset")
            if attempt >= max_retries:
                resp.raise_for_status()
            # compute sleep
            sleep_s = 60
            if reset and reset.isdigit():
                try:
                    reset_epoch = int(reset)
                    sleep_s = max(10, reset_epoch - int(time.time()))
                except Exception:
                    sleep_s = 60 * (attempt + 1)
            else:
                sleep_s = 60 * (attempt + 1)
            time.sleep(sleep_s)
            attempt += 1
            continue
        resp.raise_for_status()
        return resp.json()


def normalize_query(keywords: List[str]) -> str:
    # Build safe OR query, quoting terms with spaces
    parts = []
    for k in keywords:
        k = k.strip()
        if not k:
            continue
        if " " in k and not (k.startswith("from:") or k.startswith("to:") or k.startswith("@")):
            parts.append(f'"{k}"')
        else:
            parts.append(k)
    return " OR ".join(parts)


# -----------------------------
# Optional source: snscrape (no API key required)
# -----------------------------

def search_recent_snscrape(query: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent tweets using snscrape and return normalized list.

    Note: Install optional extra 'scrape' → pip install docmaplabs-marketing-package[scrape]
    """
    try:
        import itertools
        import snscrape.modules.twitter as sntwitter  # type: ignore
    except Exception as e:  # pragma: no cover - optional dependency
        raise RuntimeError("Install optional extras: pip install docmaplabs-marketing-package[scrape]") from e

    scraper = sntwitter.TwitterSearchScraper(query)
    items = itertools.islice(scraper.get_items(), max_results)
    out: List[Dict[str, Any]] = []
    for tw in items:
        # tw is a Tweet object with attributes id, user, date, rawContent, likeCount, retweetCount, replyCount, quoteCount
        metrics = {
            "like_count": getattr(tw, "likeCount", None),
            "retweet_count": getattr(tw, "retweetCount", None),
            "reply_count": getattr(tw, "replyCount", None),
            "quote_count": getattr(tw, "quoteCount", None),
        }
        out.append({
            "id": str(getattr(tw, "id", None) or ""),
            "author": f"@{getattr(getattr(tw, 'user', None), 'username', '')}" if getattr(getattr(tw, 'user', None), 'username', '') else None,
            "text": getattr(tw, "rawContent", None) or getattr(tw, "content", None),
            "createdAt": getattr(tw, "date", None).isoformat() if getattr(tw, "date", None) else None,
            "metrics": metrics,
        })
    return out

