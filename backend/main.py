from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import EvaluateRequest, EvaluateResponse, ConsistencyResult, EvidenceItem, ConstraintItem
from chunker import chunk_novel, count_tokens
from pathway_pipeline import run_pathway_pipeline
from llm_client import evaluate_backstory

app = FastAPI(
    title="Narrative Consistency Checker API",
    description="Evaluates character backstory consistency against novel constraints",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_consistency(request: EvaluateRequest):
    """
    Evaluate whether a hypothetical character backstory is logically consistent
    with a complete long-form novel.
    
    Processing Pipeline:
    1. Chunk the novel into 2-3k token segments
    2. Ingest chunks into Pathway table
    3. Extract constraints per chunk via LLM (Pathway transformation)
    4. Aggregate constraints using Pathway reducers
    5. Evaluate backstory against aggregated constraints via LLM
    """
    
    if not request.novel_text.strip():
        raise HTTPException(status_code=400, detail="Novel text cannot be empty")
    if not request.backstory.strip():
        raise HTTPException(status_code=400, detail="Backstory cannot be empty")
    
    novel_tokens = count_tokens(request.novel_text)
    if novel_tokens < 100:
        raise HTTPException(status_code=400, detail="Novel text too short for meaningful analysis")
    
    # Step 1: Chunk the novel
    chunks = chunk_novel(request.novel_text)
    
    # Steps 2-4: Run Pathway pipeline (ingestion, transformation, aggregation)
    aggregated_constraints = run_pathway_pipeline(chunks)
    
    # Step 5: Evaluate backstory against constraints (LLM Call #2)
    evaluation_result = evaluate_backstory(aggregated_constraints, request.backstory)
    
    # Map verdict to binary prediction (1 = consistent, 0 = inconsistent)
    raw_verdict = evaluation_result.get("verdict", "INCONSISTENT")
    # Normalize: WEAKLY CONSISTENT counts as INCONSISTENT (binary output)
    verdict = "CONSISTENT" if raw_verdict == "CONSISTENT" else "INCONSISTENT"
    prediction = 1 if verdict == "CONSISTENT" else 0
    
    # Build response
    reasoning_data = evaluation_result.get("reasoning", {})
    reasoning = ConsistencyResult(
        temporal_consistency=reasoning_data.get("temporal_consistency", "No analysis available"),
        causal_reasoning=reasoning_data.get("causal_reasoning", "No analysis available"),
        narrative_constraints=reasoning_data.get("narrative_constraints", "No analysis available")
    )
    
    evidence = [
        EvidenceItem(
            claim=e.get("claim", ""),
            evidence=e.get("evidence", ""),
            supports=e.get("supports", False)
        )
        for e in evaluation_result.get("evidence", [])
    ]
    
    constraint_items = [
        ConstraintItem(
            type=item["type"],
            description=item["description"],
            chunk_ids=item["chunk_ids"]
        )
        for item in aggregated_constraints.get("items", [])
    ]
    
    return EvaluateResponse(
        verdict=verdict,
        prediction=prediction,
        reasoning=reasoning,
        evidence=evidence,
        aggregated_constraints=constraint_items
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
