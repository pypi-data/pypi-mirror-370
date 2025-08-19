# DocmapLabs Marketing Package

A pip-installable toolkit to discover relevant healthcare posts and extract leads using either:
- an OpenRouter LLM for insights/summaries, and/or
- your Hugging Face multi-head leads classifier (intent + symptoms + specialties).

Optional connectors save to Airtable/CSV/SQLite and sync contacts to HubSpot. Includes a FastAPI server, a rate-limit-aware CLI, and an optional poller.

## Install

```bash
# core
python -m pip install --user docmaplabs-marketing-package
# extras
python -m pip install --user "docmaplabs-marketing-package[server]"   # FastAPI
python -m pip install --user "docmaplabs-marketing-package[ml]"       # HF model inference
python -m pip install --user "docmaplabs-marketing-package[scrape]"   # snscrape (optional)
```

Python >= 3.8. Add user bin to PATH if needed: `export PATH="$HOME/.local/bin:$PATH"`.

## Environment variables (set only what you need)

- OpenRouter (LLM)
  - `OPENROUTER_API_KEY` (required for real LLM results)
  - `OPENROUTER_MODEL` (default: `meta-llama/llama-3.1-8b-instruct:free`)
- Twitter fetch (optional, for CLI fetch)
  - `TWITTER_BEARER_TOKEN` (App-only bearer token)
- Hugging Face classifier (optional)
  - `HF_LEADS_REPO_ID` (e.g., `your-org/docmap-leads-classifier-v1`)
  - `LEADS_THRESHOLD` (default `0.3`), `LEADS_DEVICE` (`auto|cpu|cuda`), `LEADS_BASE_MODEL` (default `microsoft/deberta-v3-base`)
- Airtable (optional)
  - `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`
  - `AIRTABLE_TABLE_HEALTHCARE_INSIGHTS` (default `Healthcare Insights`)
  - `AIRTABLE_TABLE_LEADS` (default `Leads`)
- HubSpot (optional)
  - `HUBSPOT_ACCESS_TOKEN` (private app token; contacts read/write)

Tokens are function-scoped. If a token is missing and a feature needs it, that feature is skipped or a clear error is raised. LLM calls fallback to simple heuristics if `OPENROUTER_API_KEY` is absent. You can interactively create a `.env` via `--prompt-creds` and/or load an env via `--env-file`.

## CLI usage

Analyze existing posts (from file or stdin) and save insights:
```bash
docmaplabs-marketing analyze-healthcare \
  --tweets ./tweets.json \
  --keywords NHS "waiting times" GP \
  --region UK \
  --save csv:/tmp/insights.csv \
  --out /tmp/analysis.json
```

End-to-end: fetch → analyze → save insights and leads (rate-limit aware):
```bash
docmaplabs-marketing run-keywords \
  --keywords NHS "waiting times" GP \
  --region UK \
  --analysis-save csv:/tmp/insights.csv \
  --lead-csv /tmp/leads.csv \
  --lead-airtable \
  --lead-hubspot \
  --prompt-creds     # interactively prompt for missing tokens and optionally save to ~/.docmaplabs_marketing/.env
  --env-file /path/to/.env   # load a specific env profile (per account/workspace)
```

Storage targets:
- Insights: `airtable` | `csv:/path/file.csv` | `sqlite:/path/db.sqlite[::table]`
- Leads: `--lead-csv` path, `--lead-airtable`, `--lead-hubspot`

Notes:
- If your Python lacks SQLite, use CSV/Airtable (the tool reports a clear error otherwise).
- Twitter Free tier rate limits apply; the client backs off automatically using reset headers (429-aware with reset).
- snscrape is provided as best-effort (`--source snscrape`). It may break due to upstream changes; prefer the Twitter API for reliability.

## Server (FastAPI)

```bash
docmaplabs-marketing-api --host 0.0.0.0 --port 8000
```

Endpoints:
- GET `/health` → `{ ok: true }`
- POST `/analyze-healthcare`
  - Body: `{ "tweets": [string | {id, author|handle|user, text}], "keywords": [string], "region": "UK" }`
  - Returns `HealthcareAnalysis` and attempts to save insights to Airtable if configured
- POST `/generate-travel-advice`
  - Body: `{ "query": "Tokyo 3 days", "triggerUser": "@you" }`
  - Returns `Advice`
- POST `/classify-posts`
  - Body: `{ "texts": ["post text", ...], "threshold": 0.3 }`
  - Returns `{ predictions: [{ intent, symptoms[], specialties[] }, ...] }`

### Using the DocMap UK triage model (optional)
- Recommended HF repo: `rabbitfishai/docmap-uk-triage-merged-qwen2.5-7b`
- Configure via env or pyproject:
  - Env: `HF_TRIAGE_REPO_ID=...` (or `HF_TRIAGE_ENDPOINT` for a private HF Inference Endpoint), optional `HUGGINGFACEHUB_API_TOKEN`.
  - Pyproject defaults: under `[tool.docmaplabs_marketing]` set `triage_repo_id`, `triage_system_prompt`.
- Intended use and safety:
  - Informational guidance; not a diagnosis. For life-threatening emergencies call 999; for urgent concerns call 111. Not affiliated with the NHS.
  - Add this disclaimer in your UI/API and logs.

## Python API (library)

```python
from docmaplabs_marketing_package.agent import analyze_healthcare_tweets, generate_travel_advice
from docmaplabs_marketing_package.leadgen import extract_leads, classify_posts_with_hf

# Analyze tweets
tweets = [
  {"id":"1","author":"@nhs_user","text":"GP appointments delayed again."},
  "Hospitals in London facing staffing issues",
]
analysis = analyze_healthcare_tweets(tweets, keywords=["NHS","waiting times"], region="UK")
leads = extract_leads(analysis, min_relevance=0.6)

# HF classifier
preds = classify_posts_with_hf(["Any advice on fever? Based in Glasgow"], threshold=0.3)

# Travel advice
advice = generate_travel_advice("Tokyo 3 days in October", "@you")
print(advice.summary)
```

### Data models
- `HealthcareAnalysis` → `summary: str`, `insights: List[HealthcareInsight]`
- `HealthcareInsight` → `tweetId, author, text, isHealthcareRelated, isUKRelated, categories[], painPoints[], sentiment, urgency, relevance, contacts[]`
- `Lead` → `handle, name?, sourceTweetId?, relevance, notes?`
- `Advice` → `title, summary, itinerary[{day,plan}], costEstimateUSD?, confidence?`

## Airtable schema (optional)

Create:
- `Healthcare Insights` with: `TweetId`, `Author`, `Text` (long text), `IsHealthcareRelated` (checkbox), `IsUKRelated` (checkbox), `Categories`, `PainPoints`, `Sentiment`, `Urgency` (number), `Relevance` (number), `Contacts`, `Summary` (long text)
- `Leads` with: `Handle`, `Name`, `SourceTweetId`, `Relevance` (number), `Notes`

## Poller (optional, rate-limit aware)

Runs a loop that:
- fetches with backoff (Twitter API),
- analyzes with OpenRouter (or heuristic fallback),
- extracts leads, and
- persists `since_id` under `~/.cache/docmaplabs_marketing/` to avoid reprocessing.

```bash
docmaplabs-marketing-poller
# configure with env (.env or --env-file) and POLL_INTERVAL_SECONDS (default 60)
```

Each iteration prints a JSON line like:
```json
{ "fetched": 50, "leads": 7, "newest_id": "1871234" }
```

You can also import and call `poller.run(once=True, keywords=[...])` in Python.

## Safety and Intended Use (UK)
- This toolkit and any referenced models provide general information and lead identification; they are not medical devices.
- Do not use for diagnosis or emergency triage. For life‑threatening emergencies, call 999; for urgent concerns, call 111.
- Ensure GDPR/DPA compliance, publish a privacy policy, and obtain consent where required (e.g., direct outreach).
- Advertising: follow CAP/ASA rules; avoid implying NHS endorsement.

## Changelog
- 0.2.0: HF classifier integration, `/classify-posts` endpoint, snscrape optional source, Twitter API rate-limit backoff, env-file support, poller with since_id state, docs polish, packaging metadata, `[all]` extra.
- 0.1.0: Initial public version with CLI, FastAPI, Airtable/CSV/SQLite storage, HubSpot sync (optional), and Twitter fetch.

## License
MIT
Open Source Package for Marketing
