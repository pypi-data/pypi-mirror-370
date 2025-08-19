import json
import requests
from .config import settings
from .models import Advice, HealthcareAnalysis


def generate_travel_advice(query: str, lead_handle: str | None = None) -> Advice:
    if not settings.openrouter.api_key:
        return Advice(title="Sample Itinerary", summary="Dev mode. Set OPENROUTER_API_KEY to enable real advice.", itinerary=[{"day":1,"plan":"Arrival and check-in"}], confidence=0.4)  # type: ignore
    system = "Return ONLY valid JSON with keys: title, summary, itinerary (list of {day, plan}), costEstimateUSD (optional), confidence (0-1)."
    prompt = f"User{(' ' + lead_handle) if lead_handle else ''}: {query}"
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "DocmapLabs Marketing Agent",
        },
        json={
            "model": settings.openrouter.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
        timeout=30,
    )
    resp.raise_for_status()
    text = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "{}")
    try:
        data = json.loads(text)
        return Advice.model_validate(data)
    except Exception:
        return Advice(title="Travel Plan", summary="Parsing error", itinerary=[], confidence=0)


def analyze_healthcare_tweets(
    tweets: list[dict | str],
    keywords: list[str] | None = None,
    region: str = "UK",
) -> HealthcareAnalysis:
    """
    Analyze tweets for healthcare-related pain points (focus on UK by default).
    tweets: list of raw strings or dicts with keys {id, author, text}
    Returns structured JSON with insights and a brief summary.
    """
    # Normalize tweets into compact lines for the prompt
    def norm(t: dict | str, idx: int) -> str:
        if isinstance(t, dict):
            tid = t.get("id") or f"t{idx}"
            author = t.get("author") or t.get("handle") or t.get("user") or "@unknown"
            text = t.get("text") or ""
            return f"[{tid}] {author}: {text}"
        return f"[t{idx}] {t}"

    prompt_tweets = "\n".join(norm(t, i) for i, t in enumerate(tweets[:25])) or "(no tweets provided)"
    kw = ", ".join(keywords or ["healthcare", "NHS", "waiting times", "GP", "hospital", "UK"])

    if not settings.openrouter.api_key:
        # Heuristic fallback: keyword match to build a minimal summary
        lower = [str(t).lower() for t in tweets]
        hits = [t for t in lower if any(k in t for k in ["nhs", "wait", "gp", "appointment", "hospital", "uk"])]
        return HealthcareAnalysis(summary=f"Heuristic summary: {len(hits)} of {len(lower)} tweets mention UK healthcare-related terms.", insights=[])

    system = (
        "You are a healthcare market research analyst focused on the UK. "
        "Given tweets, extract structured insights about pain points, themes, and potential contacts. "
        "Return ONLY valid JSON with keys: summary (string), insights (array of objects). "
        "Each insight object must have: tweetId (string), author (string), text (string), "
        "isHealthcareRelated (boolean), isUKRelated (boolean), categories (string[]), painPoints (string[]), "
        "sentiment (one of: negative, neutral, positive), urgency (0-1), relevance (0-1), contacts (string[])."
    )
    user = (
        f"Keywords: {kw}\n"
        f"Region: {region}\n"
        f"Tweets:\n{prompt_tweets}\n"
        "Respond with compact JSON only."
    )

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "DocmapLabs Healthcare Insights",
        },
        json={
            "model": settings.openrouter.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    resp.raise_for_status()
    text = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "{}")
    try:
        data = json.loads(text)
        return HealthcareAnalysis.model_validate(data)
    except Exception:
        return HealthcareAnalysis(summary="Parsing error", insights=[])


