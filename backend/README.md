# Narrative Consistency Checker - Backend

## Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
copy .env.example .env
# Edit .env with your API key
```

4. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoint

POST `/evaluate`
- Input: `{ "novel_text": "...", "backstory": "..." }`
- Output: Verdict, reasoning, evidence, and extracted constraints
