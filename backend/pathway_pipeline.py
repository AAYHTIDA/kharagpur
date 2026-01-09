"""
Pathway pipeline for constraint extraction and aggregation.
Uses real Pathway tables, UDFs, and reducers.
"""
import pathway as pw
import json
import time
from llm_client import extract_constraints


# Define schema for novel chunks
class ChunkSchema(pw.Schema):
    chunk_id: int
    chunk_text: str


# Define schema for constraints output
class ConstraintOutputSchema(pw.Schema):
    chunk_id: int
    constraints_json: str


def run_pathway_pipeline(chunks: list[dict], backstory: str = "") -> dict:
    print("=" * 50)
    print("PATHWAY PIPELINE STARTED")
    print(f"Ingesting {len(chunks)} chunks into Pathway table...")
    print("=" * 50)
    
    # Step 1: Ingest chunks into Pathway table
    chunk_rows = [
        (c["chunk_id"], c["chunk_text"])
        for c in chunks
    ]
    
    chunk_table = pw.debug.table_from_rows(
        schema=ChunkSchema,
        rows=chunk_rows
    )
    print(f"[PATHWAY] Created chunk_table with {len(chunk_rows)} rows")
    
    total_chunks = len(chunks)
    
    # Step 2: Define Pathway UDF for LLM constraint extraction
    @pw.udf
    def extract_constraints_udf(chunk_id: int, chunk_text: str) -> str:
        """Pathway UDF for extracting constraints from a chunk."""
        print(f"Processing chunk {chunk_id + 1}/{total_chunks}...")
        result = extract_constraints(chunk_id, chunk_text)
        time.sleep(3)  # Balance between speed and rate limits
        return json.dumps(result)
    
    # Step 3: Apply Pathway transformation - extract constraints per chunk
    constraints_table = chunk_table.select(
        chunk_id=pw.this.chunk_id,
        constraints_json=extract_constraints_udf(pw.this.chunk_id, pw.this.chunk_text)
    )
    
    # Step 4: Collect results - use table_to_pandas for reliable conversion
    try:
        df = pw.debug.table_to_pandas(constraints_table)
        constraint_rows = df.to_dict('records')
    except Exception as e:
        print(f"[PATHWAY] Error converting table: {e}")
        # Fallback: try table_to_dicts
        raw_result = pw.debug.table_to_dicts(constraints_table)
        print(f"[PATHWAY] Raw result type: {type(raw_result)}, content sample: {str(raw_result)[:200]}")
        constraint_rows = []
        if isinstance(raw_result, dict):
            # Column-oriented dict
            chunk_ids = raw_result.get("chunk_id", [])
            jsons = raw_result.get("constraints_json", [])
            for i in range(len(chunk_ids)):
                constraint_rows.append({"chunk_id": chunk_ids[i], "constraints_json": jsons[i]})
        elif isinstance(raw_result, list):
            if len(raw_result) > 0 and isinstance(raw_result[0], dict):
                constraint_rows = raw_result
            else:
                # List of tuples/lists
                for item in raw_result:
                    if len(item) >= 2:
                        constraint_rows.append({"chunk_id": item[0], "constraints_json": item[1]})
    
    print(f"[PATHWAY] Extracted constraints from {len(constraint_rows)} chunks")
    
    # Step 5: Parse constraints and flatten for aggregation
    flat_rows = []
    for row in constraint_rows:
        try:
            parsed = json.loads(row["constraints_json"])
            chunk_id = row["chunk_id"]
            
            for fact in parsed.get("timeline_facts", []):
                if isinstance(fact, str) and fact.strip():
                    flat_rows.append((chunk_id, "timeline_fact", fact.strip()))
            
            for trait in parsed.get("character_traits", []):
                if isinstance(trait, str) and trait.strip():
                    flat_rows.append((chunk_id, "character_trait", trait.strip()))
            
            for dep in parsed.get("causal_dependencies", []):
                if isinstance(dep, str) and dep.strip():
                    flat_rows.append((chunk_id, "causal_dependency", dep.strip()))
            
            for lim in parsed.get("narrative_limitations", []):
                if isinstance(lim, str) and lim.strip():
                    flat_rows.append((chunk_id, "narrative_limitation", lim.strip()))
        except Exception as e:
            print(f"[PATHWAY] Error parsing constraint: {e}")
            continue
    
    if not flat_rows:
        print("[PATHWAY] No constraints extracted, returning empty result")
        return {
            "timeline_facts": [],
            "character_traits": [],
            "causal_dependencies": [],
            "narrative_limitations": [],
            "items": [],
            "total_chunks_processed": len(chunks)
        }
    
    # Step 6: Create Pathway table for aggregation
    class FlatConstraintSchema(pw.Schema):
        chunk_id: int
        constraint_type: str
        description: str
    
    flat_table = pw.debug.table_from_rows(
        schema=FlatConstraintSchema,
        rows=flat_rows
    )
    print(f"[PATHWAY] Created flat_table with {len(flat_rows)} constraint rows")
    
    # Step 7: Pathway groupby + reduce for deduplication and aggregation
    print("[PATHWAY] Running groupby().reduce() for constraint aggregation...")
    grouped_table = flat_table.groupby(
        flat_table.constraint_type,
        flat_table.description
    ).reduce(
        constraint_type=pw.this.constraint_type,
        description=pw.this.description,
        chunk_ids=pw.reducers.sorted_tuple(pw.this.chunk_id)
    )
    
    # Step 8: Collect aggregated results
    try:
        agg_df = pw.debug.table_to_pandas(grouped_table)
        aggregated_rows = agg_df.to_dict('records')
    except Exception as e:
        print(f"[PATHWAY] Error converting aggregated table: {e}")
        aggregated_rows = []
    
    print(f"[PATHWAY] Aggregated into {len(aggregated_rows)} unique constraints")
    
    # Step 9: Build final structure
    timeline_facts = []
    character_traits = []
    causal_dependencies = []
    narrative_limitations = []
    items = []
    
    for row in aggregated_rows:
        chunk_ids = list(set(row.get("chunk_ids", [])))
        item = {
            "type": row["constraint_type"],
            "description": row["description"],
            "chunk_ids": sorted(chunk_ids) if chunk_ids else []
        }
        items.append(item)
        
        if row["constraint_type"] == "timeline_fact":
            timeline_facts.append(row["description"])
        elif row["constraint_type"] == "character_trait":
            character_traits.append(row["description"])
        elif row["constraint_type"] == "causal_dependency":
            causal_dependencies.append(row["description"])
        elif row["constraint_type"] == "narrative_limitation":
            narrative_limitations.append(row["description"])
    
    print("=" * 50)
    print("PATHWAY PIPELINE COMPLETED")
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
