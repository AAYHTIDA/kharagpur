import json
import requests
import time

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"

CONSTRAINT_EXTRACTION_PROMPT = """Analyze this novel chunk and extract key narrative constraints. Be concise.

CHUNK TEXT:
{chunk_text}

Return ONLY a JSON object:
{{
  "timeline_facts": ["max 3 key dates/ages/periods"],
  "character_traits": ["max 3 key traits"],
  "causal_dependencies": ["max 3 cause-effect relationships"],
  "narrative_limitations": ["max 3 rules/constraints"]
}}

Return ONLY valid JSON."""

EVALUATION_PROMPT = """Evaluate if this backstory is consistent with the novel constraints.

CONSTRAINTS:
{constraints}

BACKSTORY:
{backstory}

Return ONLY a JSON object:
{{
  "verdict": "CONSISTENT" or "INCONSISTENT",
  "reasoning": {{
    "temporal_consistency": "brief analysis",
    "causal_reasoning": "brief analysis",
    "narrative_constraints": "brief analysis"
  }},
  "evidence": [
    {{"claim": "claim", "evidence": "evidence", "supports": true/false}}
  ]
}}

Return ONLY valid JSON."""


def call_llm(prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = requests.post(
                GROQ_API_URL,
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < retries - 1:
                print(f"Rate limited, waiting 15 seconds...")
                time.sleep(15)
                continue
            raise Exception(f"Groq API error: {e.response.status_code} - {e.response.text}")
    raise Exception("Max retries exceeded")


def parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return json.loads(text)


def extract_constraints(chunk_id: int, chunk_text: str) -> dict:
    prompt = CONSTRAINT_EXTRACTION_PROMPT.format(chunk_text=chunk_text[:1500])
    try:
        response_text = call_llm(prompt)
        result = parse_json_response(response_text)
        result["chunk_id"] = chunk_id
        return result
    except Exception as e:
        return {
            "chunk_id": chunk_id,
            "timeline_facts": [],
            "character_traits": [],
            "causal_dependencies": [],
            "narrative_limitations": [],
            "error": str(e)
        }


def limit_constraints(constraints: dict, max_items: int = 10) -> dict:
    return {
        "timeline_facts": constraints.get("timeline_facts", [])[:max_items],
        "character_traits": constraints.get("character_traits", [])[:max_items],
        "causal_dependencies": constraints.get("causal_dependencies", [])[:max_items],
        "narrative_limitations": constraints.get("narrative_limitations", [])[:max_items]
    }


def evaluate_backstory(constraints: dict, backstory: str) -> dict:
    limited = limit_constraints(constraints, max_items=10)
    prompt = EVALUATION_PROMPT.format(
        constraints=json.dumps(limited),
        backstory=backstory[:1500]
    )
    try:
        response_text = call_llm(prompt)
        return parse_json_response(response_text)
    except Exception as e:
        return {
            "verdict": "INCONSISTENT",
            "reasoning": {
                "temporal_consistency": f"Error: {str(e)}",
                "causal_reasoning": "Unable to complete",
                "narrative_constraints": "Unable to complete"
            },
            "evidence": []
        }
