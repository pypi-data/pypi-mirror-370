import sys, json
import argparse
from .agent import analyze_healthcare_tweets
from .models import HealthcareAnalysis
from .storage import save_healthcare_analysis, save_leads_to_csv, save_leads_to_airtable
from .leadgen import extract_leads, classify_posts_with_hf
from .twitter_client import search_recent, normalize_tweets, search_recent_snscrape, search_recent_with_backoff, normalize_query
from .services.hubspot import save_leads_to_hubspot
from .creds import prompt_for_env, save_env_file


def run():
    p = argparse.ArgumentParser(prog="docmaplabs-marketing")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze-healthcare", help="Analyze tweets for healthcare pain points")
    a.add_argument("--tweets", help="Path to JSON file with tweets (list of strings or dicts). If omitted, read from stdin")
    a.add_argument("--keywords", nargs="*", help="Keywords list")
    a.add_argument("--region", default="UK")
    a.add_argument("--out", help="Write results to path (json). If omitted, print to stdout")
    a.add_argument("--save", help="Storage target: airtable | csv:/path/file.csv | sqlite:/path/db.sqlite[::table]")

    k = sub.add_parser("run-keywords", help="Fetch, analyze, and save leads for keywords")
    k.add_argument("--keywords", nargs="+", required=True)
    k.add_argument("--region", default="UK")
    k.add_argument("--since-id", help="Optional since_id for incremental fetching")
    k.add_argument("--lead-csv", help="CSV path to append extracted leads")
    k.add_argument("--lead-airtable", action="store_true", help="Also save leads to Airtable (requires env)")
    k.add_argument("--analysis-save", help="Storage target for insights: airtable|csv:...|sqlite:...")
    k.add_argument("--lead-hubspot", action="store_true", help="Also upsert leads into HubSpot (requires HUBSPOT_ACCESS_TOKEN)")
    k.add_argument("--prompt-creds", action="store_true", help="Interactively prompt for missing credentials (Twitter/Airtable/HubSpot)")
    k.add_argument("--source", choices=["twitter", "snscrape"], default="twitter", help="Data source for fetching posts")
    k.add_argument("--env-file", help="Path to a .env file to load before running")

    # Register HF classifier command before parsing
    cp = sub.add_parser("classify-posts", help="Classify raw texts with HF leads classifier")
    cp.add_argument("texts", nargs="+", help="Texts to classify")
    cp.add_argument("--threshold", type=float, default=None)

    args = p.parse_args()
    if args.cmd == "analyze-healthcare":
        if args.tweets:
            with open(args.tweets, "r", encoding="utf-8") as f:
                tweets = json.load(f)
        else:
            tweets = json.load(sys.stdin)
        analysis: HealthcareAnalysis = analyze_healthcare_tweets(tweets, args.keywords, args.region)
        if args.save:
            save_healthcare_analysis(args.save, analysis)
        data = analysis.model_dump()
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
            print()
    elif args.cmd == "run-keywords":
        if args.env_file:
            # Best-effort load of provided env file
            try:
                from dotenv import load_dotenv  # type: ignore
                load_dotenv(args.env_file, override=False)
                print(f"Loaded env from {args.env_file}")
            except Exception:
                pass

        if args.prompt_creds:
            updated = prompt_for_env(["TWITTER_BEARER_TOKEN", "AIRTABLE_API_KEY", "AIRTABLE_BASE_ID", "HUBSPOT_ACCESS_TOKEN", "OPENROUTER_API_KEY"])
            if updated:
                path = save_env_file(updated)
                if path:
                    print(f"Saved provided credentials to {path}")
        # Build safe OR query
        query = normalize_query(args.keywords)
        if args.source == "twitter":
            # Use backoff by default to respect rate limits
            payload = search_recent_with_backoff(query, since_id=args.since_id, max_results=50)
            tweets = normalize_tweets(payload)
        else:
            tweets = search_recent_snscrape(query, max_results=100)
        analysis: HealthcareAnalysis = analyze_healthcare_tweets(tweets, args.keywords, args.region)
        if args.analysis_save:
            save_healthcare_analysis(args.analysis_save, analysis)
        leads = extract_leads(analysis, min_relevance=0.6)
        if args.lead_csv:
            save_leads_to_csv(args.lead_csv, leads)
        if args.lead_airtable:
            save_leads_to_airtable(leads)
        if args.lead_hubspot:
            save_leads_to_hubspot(leads)
        out = {
            "since_id": (payload.get("meta", {}) or {}).get("newest_id"),
            "lead_count": len(leads),
            "source": args.source,
        }
        json.dump(out, sys.stdout, ensure_ascii=False)
        print()
    elif args.cmd == "classify-posts":
        preds = classify_posts_with_hf(args.texts, args.threshold)
        json.dump({"predictions": preds}, sys.stdout, ensure_ascii=False)
        print()


