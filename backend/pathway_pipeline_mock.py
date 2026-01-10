"""
Mock version of pathway pipeline for development/testing.
Simulates the constraint extraction and aggregation without Pathway.
"""
import json
import time
from llm_client import extract_constraints


def run_pathway_pipeline(chunks: list[dict], backstory: str = "") -> dict:
    print("=" * 50)
    print("MOCK PATHWAY PIPELINE STARTED")
    print(f"Processing {len(chunks)} chunks...")
    print("=" * 50)
    
    # Mock constraint extraction
    all_constraints = []
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{total_chunks}...")
        try:
            # Mock constraint extraction - you can replace this with actual LLM calls
            mock_result = {
                "timeline_facts": [f"Timeline fact from chunk {chunk['chunk_id']}"],
                "character_traits": [f"Character trait from chunk {chunk['chunk_id']}"],
                "causal_dependencies": [f"Causal dependency from chunk {chunk['chunk_id']}"],
                "narrative_limitations": [f"Narrative limitation from chunk {chunk['chunk_id']}"]
            }
            all_constraints.append({
                "chunk_id": chunk["chunk_id"],
                "constraints": mock_result
            })
            # Simulate processing time
            time.sleep(0.1)
        except Exception as e:
            print(f"Error processing chunk {chunk['chunk_id']}: {e}")
            continue
    
    # Aggregate constraints
    timeline_facts = []
    character_traits = []
    causal_dependencies = []
    narrative_limitations = []
    items = []
    
    for constraint_data in all_constraints:
        chunk_id = constraint_data["chunk_id"]
        constraints = constraint_data["constraints"]
        
        for fact in constraints.get("timeline_facts", []):
            timeline_facts.append(fact)
            items.append({
                "type": "timeline_fact",
                "description": fact,
                "chunk_ids": [chunk_id]
            })
        
        for trait in constraints.get("character_traits", []):
            character_traits.append(trait)
            items.append({
                "type": "character_trait", 
                "description": trait,
                "chunk_ids": [chunk_id]
            })
        
        for dep in constraints.get("causal_dependencies", []):
            causal_dependencies.append(dep)
            items.append({
                "type": "causal_dependency",
                "description": dep,
                "chunk_ids": [chunk_id]
            })
        
        for lim in constraints.get("narrative_limitations", []):
            narrative_limitations.append(lim)
            items.append({
                "type": "narrative_limitation",
                "description": lim,
                "chunk_ids": [chunk_id]
            })
    
    print("=" * 50)
    print("MOCK PATHWAY PIPELINE COMPLETED")
    print(f"Timeline facts: {len(timeline_facts)}")
    print(f"Character traits: {len(character_traits)}")
    print(f"Causal dependencies: {len(causal_dependencies)}")
    print(f"Narrative limitations: {len(narrative_limitations)}")
    print("=" * 50)
    
    return {
        "timeline_facts": timeline_facts,
        "character_traits": character_traits,
        "causal_dependencies": causal_dependencies,
        "narrative_limitations": narrative_limitations,
        "items": items,
        "total_chunks_processed": len(chunks)
    }