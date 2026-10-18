# AI Tech Consultant

An integrated prototype containing three connected workflows.

## Components

### Task 1 — Knowledge Brain
- Crawls Brilliant Directories support documentation.
- Stores articles and chunks in PostgreSQL with pgvector.
- Retrieves relevant text and generates answers with a local Ollama model.
- Exposes search and question-answering endpoints through FastAPI.

### Task 2 — Inbox Agent
- Classifies incoming support emails.
- Requests supporting knowledge from Task 1.
- Creates a reply draft for human review.
- Does not send emails automatically.

### Task 3 — Meeting-to-Scope
- Extracts candidate requirements from meeting transcripts.
- Produces provisional effort estimates.
- Checks proposed scope against the Knowledge Brain.
- Compares follow-up requests with an approved baseline.

## Local setup

Requirements: Python 3.11+, Node.js, Docker Desktop, and Ollama with `llama3.2:3b`.

### Database
From the repository root:

```powershell
docker compose up -d
```

### Task 1
```powershell
cd task1-knowledge-brain
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8002
```

API docs: http://127.0.0.1:8002/docs

If the virtual environment has not been created, run `python -m venv .venv` and `pip install -r requirements.txt` first. Keep your `.env` file local and never commit secrets.

### Task 2
Open a separate terminal:

```powershell
cd task2-inbox-agent
npm install
$env:KNOWLEDGE_API = "http://127.0.0.1:8002/query"
$env:PORT = "3002"
npm run dev
```

Health check: http://127.0.0.1:3002/health

Example request:

```powershell
$body = @{
  from = "customer@example.com"
  subject = "Invoice question"
  body = "I was charged twice. Can you check?"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://localhost:3002/process `
  -ContentType "application/json" `
  -Body $body
```

### Task 3
Open another terminal:

```powershell
cd task3-meeting-to-scope
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
```

If its virtual environment does not exist, create it first with `python -m venv .venv`.

API docs: http://127.0.0.1:8001/docs

## Tests

Task 2:
```powershell
cd task2-inbox-agent
npm test
npm run typecheck
```

Task 3:
```powershell
cd task3-meeting-to-scope
python -m pytest tests -v
```

## Documentation and data

- `shared-docs/DESIGN.md` — architecture and trust boundaries.
- `shared-docs/EVALS.md` — evaluation methodology and status.
- `shared-docs/AI_LOG.md` — development log and limitations.
- `shared-docs/evaluation/` — test prompts for all three tasks.
- `task2-inbox-agent/data/sample_emails.jsonl` — synthetic email examples.
- `task3-meeting-to-scope/transcripts/` — three synthetic meeting transcripts.

## Known limitations

- Task 2's Knowledge Brain lookup has not yet been verified end-to-end; its draft must be reviewed.
- The email classifier uses keyword rules, not a trained classifier.
- Meeting requirement extraction is heuristic.
- Estimates are provisional and require human validation.
- Evaluation datasets are test inputs, not evidence of measured performance.
- The current generation path uses local Ollama. Do not claim Claude comparisons, measured model costs, or evaluation scores unless those experiments have actually been performed.
