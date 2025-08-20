import os
import time
import sys
import json
from typing import Optional, List
from .agent import analyze_healthcare_tweets
from .leadgen import extract_leads
from .twitter_client import search_recent_with_backoff, normalize_tweets, normalize_query
from .config import settings


def _state_path(name: str) -> str:
    os.makedirs(settings.state.dir, exist_ok=True)
    return os.path.join(settings.state.dir, name)


def _load_since_id(name: str) -> Optional[str]:
    path = _state_path(f"since_{name}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip() or None
    except Exception:
        return None


def _save_since_id(name: str, since_id: Optional[str]) -> None:
    if not since_id:
        return
    path = _state_path(f"since_{name}.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(since_id)
    except Exception:
        pass


def run(once: bool = False, keywords: Optional[List[str]] = None):
    interval = max(30, settings.polling.interval_seconds)
    key = "_".join((keywords or ["default"]))
    try:
        while True:
            try:
                query = normalize_query(keywords or ["NHS", "GP", "hospital"])
                since_id = _load_since_id(key)
                payload = search_recent_with_backoff(query, since_id=since_id, max_results=50)
                tweets = normalize_tweets(payload)
                if tweets:
                    analysis = analyze_healthcare_tweets(tweets, keywords or ["NHS"], "UK")
                    leads = extract_leads(analysis, min_relevance=0.6)
                    newest = (payload.get("meta", {}) or {}).get("newest_id")
                    _save_since_id(key, newest)
                    print(json.dumps({"fetched": len(tweets), "leads": len(leads), "newest_id": newest}))
                else:
                    print(json.dumps({"fetched": 0, "leads": 0}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            if once:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        sys.exit(0)


