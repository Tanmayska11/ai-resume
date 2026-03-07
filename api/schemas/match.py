# api/schemas/match.py

from pydantic import BaseModel, Field
from typing import List



class MatchRequest(BaseModel):
    job_description: str



class MatchResponse(BaseModel):
    match_score: float
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    summary: str
