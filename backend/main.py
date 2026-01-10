from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from chunker import chunk_novel, count_tokens
from pathway_pipeline_mock import run_pathway_pipeline
from llm_client import evaluate_backstory, extract_characters_and_claims

app = FastAPI(
    title="Narrative Consistency Checker API",
    description="Evaluates character backstory consistency across novels",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluateNovelsRequest(BaseModel):
    novel1_text: str
    novel2_text: str
    novel1_name: str = "Novel 1"
    novel2_name: str = "Novel 2"


class ResultRow(BaseModel):
    id: int
    novel: str
    character: str
    chapter: str
    claim: str
    result: str  # "consistent" or "contradict"


class EvaluateNovelsResponse(BaseModel):
    results: List[ResultRow]


# New models for CSV-based evaluation
class BackstoryItem(BaseModel):
    id: str
    book_name: str
    character: str
    caption: str
    content: str


class EvaluateCsvRequest(BaseModel):
    novel1_text: str
    novel2_text: str
    novel1_name: str = "Novel 1"
    novel2_name: str = "Novel 2"
    backstories: List[BackstoryItem]


class CsvResultRow(BaseModel):
    id: str
    book_name: str
    char: str
    caption: str
    content: str
    label: str  # "consistent" or "contradict"


class EvaluateCsvResponse(BaseModel):
    results: List[CsvResultRow]


@app.post("/evaluate-novels", response_model=EvaluateNovelsResponse)
async def evaluate_novels(request: EvaluateNovelsRequest):
    """
    Compare character backstories across two novels for consistency.
    Returns a table of character claims and their consistency status.
    """
    
    if not request.novel1_text.strip():
        raise HTTPException(status_code=400, detail="Novel 1 text cannot be empty")
    if not request.novel2_text.strip():
        raise HTTPException(status_code=400, detail="Novel 2 text cannot be empty")
    
    results = []
    row_id = 1
    
    # Process Novel 1
    print(f"Processing {request.novel1_name}...")
    chunks1 = chunk_novel(request.novel1_text)
    constraints1 = run_pathway_pipeline(chunks1)
    claims1 = extract_characters_and_claims(request.novel1_text, request.novel1_name)
    
    for claim in claims1:
        eval_result = evaluate_backstory(constraints1, claim["claim"])
        verdict = eval_result.get("verdict", "INCONSISTENT")
        results.append(ResultRow(
            id=row_id,
            novel=request.novel1_name,
            character=claim["character"],
            chapter=claim.get("chapter", ""),
            claim=claim["claim"][:100] + "..." if len(claim["claim"]) > 100 else claim["claim"],
            result="consistent" if verdict == "CONSISTENT" else "contradict"
        ))
        row_id += 1
    
    # Process Novel 2
    print(f"Processing {request.novel2_name}...")
    chunks2 = chunk_novel(request.novel2_text)
    constraints2 = run_pathway_pipeline(chunks2)
    claims2 = extract_characters_and_claims(request.novel2_text, request.novel2_name)
    
    for claim in claims2:
        eval_result = evaluate_backstory(constraints2, claim["claim"])
        verdict = eval_result.get("verdict", "INCONSISTENT")
        results.append(ResultRow(
            id=row_id,
            novel=request.novel2_name,
            character=claim["character"],
            chapter=claim.get("chapter", ""),
            claim=claim["claim"][:100] + "..." if len(claim["claim"]) > 100 else claim["claim"],
            result="consistent" if verdict == "CONSISTENT" else "contradict"
        ))
        row_id += 1
    
    return EvaluateNovelsResponse(results=results)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/evaluate-csv", response_model=EvaluateCsvResponse)
async def evaluate_csv(request: EvaluateCsvRequest):
    """
    Evaluate backstories from CSV against two novels.
    Returns Story ID, Prediction (1/0), and Rationale for each backstory.
    """
    
    if not request.novel1_text.strip():
        raise HTTPException(status_code=400, detail="Novel 1 text cannot be empty")
    if not request.novel2_text.strip():
        raise HTTPException(status_code=400, detail="Novel 2 text cannot be empty")
    if not request.backstories:
        raise HTTPException(status_code=400, detail="No backstories provided")
    
    results = []
    
    # Process both novels through Pathway pipeline
    print(f"Processing {request.novel1_name}...")
    chunks1 = chunk_novel(request.novel1_text)
    constraints1 = run_pathway_pipeline(chunks1)
    
    print(f"Processing {request.novel2_name}...")
    chunks2 = chunk_novel(request.novel2_text)
    constraints2 = run_pathway_pipeline(chunks2)
    
    # Map novel names to constraints (normalize for matching)
    novel_constraints = {
        request.novel1_name.lower().strip(): constraints1,
        request.novel2_name.lower().strip(): constraints2,
    }
    
    # Evaluate each backstory
    for backstory in request.backstories:
        print(f"Evaluating backstory ID: {backstory.id}")
        
        # Find matching novel constraints
        book_key = backstory.book_name.lower().strip()
        constraints = None
        
        # Try exact match first
        if book_key in novel_constraints:
            constraints = novel_constraints[book_key]
        else:
            # Try partial match
            for name, cons in novel_constraints.items():
                if book_key in name or name in book_key:
                    constraints = cons
                    break
        
        # Default to novel1 if no match found
        if constraints is None:
            constraints = constraints1
        
        # Evaluate the backstory content
        eval_result = evaluate_backstory(constraints, backstory.content)
        verdict = eval_result.get("verdict", "INCONSISTENT")
        
        # Build rationale from reasoning
        reasoning = eval_result.get("reasoning", {})
        rationale_parts = []
        if reasoning.get("temporal_consistency"):
            rationale_parts.append(f"Temporal: {reasoning['temporal_consistency']}")
        if reasoning.get("causal_reasoning"):
            rationale_parts.append(f"Causal: {reasoning['causal_reasoning']}")
        if reasoning.get("narrative_constraints"):
            rationale_parts.append(f"Narrative: {reasoning['narrative_constraints']}")
        
        rationale = " | ".join(rationale_parts) if rationale_parts else "No detailed reasoning available"
        
        results.append(CsvResultRow(
            id=backstory.id,
            book_name=backstory.book_name,
            char=backstory.character,
            caption=backstory.caption,
            content=backstory.content[:100] + "..." if len(backstory.content) > 100 else backstory.content,
            label="consistent" if verdict == "CONSISTENT" else "contradict"
        ))
    
    return EvaluateCsvResponse(results=results)
