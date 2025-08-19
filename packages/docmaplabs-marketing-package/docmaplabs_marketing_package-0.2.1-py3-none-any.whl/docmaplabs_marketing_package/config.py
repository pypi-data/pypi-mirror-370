from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path


class OpenRouterConfig(BaseModel):
    api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    model: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")


class TwitterConfig(BaseModel):
    app_key: Optional[str] = os.getenv("TWITTER_APP_KEY")
    app_secret: Optional[str] = os.getenv("TWITTER_APP_SECRET")
    access_token: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret: Optional[str] = os.getenv("TWITTER_ACCESS_SECRET")
    bot_handle: Optional[str] = os.getenv("TWITTER_BOT_HANDLE")


class AirtableTables(BaseModel):
    leads: str = os.getenv("AIRTABLE_TABLE_LEADS", "Leads")
    requests: str = os.getenv("AIRTABLE_TABLE_REQUESTS", "Requests")
    travel_advice: str = os.getenv("AIRTABLE_TABLE_TRAVEL_ADVICE", "Travel Advice")
    categories: str = os.getenv("AIRTABLE_TABLE_CATEGORIES", "Categories")
    tweets: str = os.getenv("AIRTABLE_TABLE_TWEETS", "Tweets")
    twitter_accounts: str = os.getenv("AIRTABLE_TABLE_TWITTER_ACCOUNTS", "Twitter Accounts")
    state: str = os.getenv("AIRTABLE_TABLE_STATE", "State")
    healthcare_insights: str = os.getenv("AIRTABLE_TABLE_HEALTHCARE_INSIGHTS", "Healthcare Insights")


class AirtableConfig(BaseModel):
    api_key: Optional[str] = os.getenv("AIRTABLE_API_KEY")
    base_id: Optional[str] = os.getenv("AIRTABLE_BASE_ID")
    table_name: str = os.getenv("AIRTABLE_TABLE_NAME", "Leads")
    tables: AirtableTables = AirtableTables()


class PollingConfig(BaseModel):
    enabled: bool = os.getenv("ENABLE_POLLING", "false").lower() in {"true", "1", "yes"}
    interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))


class StateConfig(BaseModel):
    # Where to persist incremental state (since_id per query, etc.)
    dir: str = os.getenv("DOCMAP_STATE_DIR", os.path.expanduser("~/.cache/docmaplabs_marketing"))


def _load_tool_defaults() -> dict:
    """Best-effort read of pyproject.toml [tool.docmaplabs_marketing]."""
    try:
        # Python 3.11+: tomllib is stdlib; fallback to tomli if available
        try:
            import tomllib  # type: ignore
            loads = tomllib.loads
        except Exception:  # pragma: no cover - optional
            import tomli  # type: ignore
            loads = tomli.loads  # type: ignore
        root = Path.cwd() / "pyproject.toml"
        if not root.exists():
            return {}
        data = loads(root.read_text())
        tool = (data.get("tool") or {}).get("docmaplabs_marketing") or {}
        return dict(tool)
    except Exception:
        return {}


_TOOL_DEFAULTS = _load_tool_defaults()


class HFLeadsConfig(BaseModel):
    repo_id: Optional[str] = os.getenv("HF_LEADS_REPO_ID") or _TOOL_DEFAULTS.get("hf_leads_repo_id")
    base_model: str = os.getenv("LEADS_BASE_MODEL", _TOOL_DEFAULTS.get("leads_base_model", "microsoft/deberta-v3-base"))
    threshold: float = float(os.getenv("LEADS_THRESHOLD", str(_TOOL_DEFAULTS.get("leads_threshold", 0.3))))
    device: str = os.getenv("LEADS_DEVICE", _TOOL_DEFAULTS.get("leads_device", "auto"))  # auto|cpu|cuda


class Settings(BaseModel):
    openrouter: OpenRouterConfig = OpenRouterConfig()
    twitter: TwitterConfig = TwitterConfig()
    airtable: AirtableConfig = AirtableConfig()
    polling: PollingConfig = PollingConfig()
    state: StateConfig = StateConfig()
    # Hugging Face leads classifier
    leads: HFLeadsConfig = HFLeadsConfig()
    # Hugging Face triage reasoning
    class TriageConfig(BaseModel):
        repo_id: Optional[str] = os.getenv("HF_TRIAGE_REPO_ID") or _TOOL_DEFAULTS.get("triage_repo_id")
        endpoint_url: Optional[str] = os.getenv("HF_TRIAGE_ENDPOINT") or _TOOL_DEFAULTS.get("triage_endpoint")
        hf_token: Optional[str] = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HF_TOKEN")
        system_prompt: str = os.getenv("TRIAGE_SYSTEM_PROMPT", _TOOL_DEFAULTS.get("triage_system_prompt", (
            "You are a UK NHS-style triage assistant. Provide general information only, not a diagnosis. "
            "For life-threatening symptoms advise calling 999 immediately; for urgent concerns advise 111. "
            "For non-urgent issues suggest GP/Pharmacy/UTC as appropriate. Be concise and risk-aware."
        )))
    triage: "Settings.TriageConfig" = TriageConfig()


settings = Settings()


