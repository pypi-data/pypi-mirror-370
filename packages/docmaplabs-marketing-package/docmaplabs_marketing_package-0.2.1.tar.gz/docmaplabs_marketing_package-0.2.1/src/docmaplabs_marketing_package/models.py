from typing import List, Optional
from pydantic import BaseModel, Field


class ItineraryItem(BaseModel):
    day: int
    plan: str


class Advice(BaseModel):
    title: str
    summary: str
    itinerary: List[ItineraryItem] = Field(default_factory=list)
    costEstimateUSD: Optional[float] = None
    confidence: Optional[float] = None


class HealthcareInsight(BaseModel):
    tweetId: str
    author: str
    text: str
    isHealthcareRelated: bool
    isUKRelated: bool
    categories: List[str] = Field(default_factory=list)
    painPoints: List[str] = Field(default_factory=list)
    sentiment: str
    urgency: float = 0.0
    relevance: float = 0.0
    contacts: List[str] = Field(default_factory=list)


class HealthcareAnalysis(BaseModel):
    summary: str
    insights: List[HealthcareInsight] = Field(default_factory=list)


class Lead(BaseModel):
    handle: str
    name: Optional[str] = None
    sourceTweetId: Optional[str] = None
    relevance: float = 0.0
    notes: Optional[str] = None


