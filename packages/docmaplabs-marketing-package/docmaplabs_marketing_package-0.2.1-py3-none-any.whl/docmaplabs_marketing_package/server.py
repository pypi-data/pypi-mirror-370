from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import generate_travel_advice, analyze_healthcare_tweets
from .leadgen import classify_posts_with_hf
from .services.airtable import save_healthcare_insights
from .models import Advice, HealthcareAnalysis


class AdviceReq(BaseModel):
    query: str
    triggerUser: str | None = None


app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/generate-travel-advice", response_model=Advice)
def gen(req: AdviceReq) -> Advice:
    try:
        advice = generate_travel_advice(req.query, req.triggerUser)
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class HealthcareReq(BaseModel):
    tweets: list[dict | str]
    keywords: list[str] | None = None
    region: str = "UK"


@app.post("/analyze-healthcare", response_model=HealthcareAnalysis)
def analyze(req: HealthcareReq) -> HealthcareAnalysis:
    try:
        data = analyze_healthcare_tweets(req.tweets, req.keywords, req.region)
        # Attempt to save into Airtable if configured
        try:
            _ = save_healthcare_insights(data.get("summary", ""), data.get("insights", []) )
        except Exception:
            pass
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class HFClassifyReq(BaseModel):
    texts: list[str]
    threshold: float | None = None


@app.post("/classify-posts")
def classify_posts(req: HFClassifyReq):
    try:
        preds = classify_posts_with_hf(req.texts, req.threshold)
        return {"predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


