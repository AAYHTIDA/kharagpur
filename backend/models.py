from pydantic import BaseModel
from typing import Literal

class EvaluateRequest(BaseModel):
    novel_text: str
    backstory: str

class ConstraintItem(BaseModel):
    type: str
    description: str
    chunk_ids: list[int]

class EvidenceItem(BaseModel):
    claim: str
    evidence: str
    supports: bool

class ConsistencyResult(BaseModel):
    temporal_consistency: str
    causal_reasoning: str
    narrative_constraints: str

class EvaluateResponse(BaseModel):
    verdict: Literal["CONSISTENT", "INCONSISTENT"]
    prediction: Literal[0, 1]  # 1 = consistent, 0 = inconsistent
    reasoning: ConsistencyResult
    evidence: list[EvidenceItem]
    aggregated_constraints: list[ConstraintItem]
