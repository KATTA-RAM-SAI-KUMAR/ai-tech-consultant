
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.retrieval import search_knowledge
from app.generation import generate_answer

app = FastAPI(
    title="AI Tech Consultant - Knowledge Brain",
    version="0.3.0",
    description="Shared knowledge API for the AI Tech Consultant",
)


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class Source(BaseModel):
    title: str
    url: str
    similarity: float


class QueryResponse(BaseModel):
    answer: str
    status: str
    sources: list[Source]
    needs_human: bool


@app.get("/")
def home():
    return {
        "message": "AI Tech Consultant Knowledge Brain API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "knowledge-brain"}


@app.get("/search")
def search(
    question: str = Query(min_length=3, max_length=2000),
    top_k: int = Query(default=5, ge=1, le=10),
):
    try:
        results = search_knowledge(question, top_k)
        return {
            "question": question,
            "count": len(results),
            "results": results,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Knowledge retrieval failed. Check server logs.",
        ) from exc


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        results = search_knowledge(request.question, top_k=8)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Knowledge retrieval failed. Check server logs.",
        ) from exc

    # Deduplicate sources by URL.
    unique_results = []
    seen_urls = set()

    for result in results:
        if result["url"] not in seen_urls:
            seen_urls.add(result["url"])
            unique_results.append(result)

    relevant = [
        result for result in unique_results
        if result["similarity"] >= 0.35
    ][:5]

    if not relevant:
        return QueryResponse(
            answer=(
                "I couldn't find sufficiently relevant documentation. "
                "Please ask a human expert."
            ),
            status="insufficient_evidence",
            sources=[],
            needs_human=True,
        )

    sources = [
        Source(
            title=result["title"],
            url=result["url"],
            similarity=result["similarity"],
        )
        for result in relevant
    ]

    evidence = "\n\n".join(
        f"[S{i}] Title: {result['title']}\n"
        f"URL: {result['url']}\n"
        f"Excerpt: {result['snippet'][:1800]}"
        for i, result in enumerate(relevant, start=1)
    )

    try:
        answer = generate_answer(request.question, evidence)
    except Exception:
        return QueryResponse(
            answer=(
                "Answer generation is unavailable. Please review the "
                "retrieved source links or ask a human expert."
            ),
            status="generation_failed",
            sources=sources,
            needs_human=True,
        )

    return QueryResponse(
        answer=answer,
        status="answered",
        sources=sources,
        needs_human=True,
    )
