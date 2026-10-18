from fastapi import FastAPI
from pydantic import BaseModel, Field
from agents.pipeline import create_scope, compare_with_baseline

app = FastAPI(title="AI Tech Consultant - Meeting to Scope", version="0.1.0")

class TranscriptRequest(BaseModel):
    transcript: str = Field(min_length=20, max_length=100000)

class CompareRequest(BaseModel):
    approved_baseline: list[str]
    follow_up_items: list[str]

@app.get("/health")
def health():
    return {"status": "ok", "service": "meeting-to-scope"}

@app.post("/scope")
def scope(request: TranscriptRequest):
    return create_scope(request.transcript)

@app.post("/compare")
def compare(request: CompareRequest):
    return compare_with_baseline(request.approved_baseline, request.follow_up_items)
