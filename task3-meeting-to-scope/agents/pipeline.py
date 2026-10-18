from dataclasses import dataclass, asdict
from typing import Any
import json
import re
import urllib.request
import urllib.error

KNOWLEDGE_API = "http://127.0.0.1:8000/query"


def extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from an agent output, failing clearly if malformed."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Agent output did not contain valid JSON")
        return json.loads(match.group(0))


def check_capabilities(scope_text: str) -> dict[str, Any]:
    """Consult Task 1 instead of assuming product capabilities."""
    payload = json.dumps({"question": f"Based on the support documentation, which product capabilities support this proposed scope? Identify unknowns and cite sources. Scope: {scope_text}"}).encode()
    request = urllib.request.Request(
        KNOWLEDGE_API, data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode())
            return result
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "status": "knowledge_api_unavailable",
            "answer": "Capability verification could not be completed. Human review is required.",
            "sources": [],
            "error": str(exc)
        }


def estimate_hours(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Transparent baseline estimate; humans must validate assumptions."""
    total = 0.0
    output = []
    for task in tasks:
        name = str(task.get("task", "Unspecified task"))
        hours = max(0.0, float(task.get("hours", 0)))
        confidence = str(task.get("confidence", "low"))
        output.append({"task": name, "hours": hours, "confidence": confidence})
        total += hours
    return {"tasks": output, "total_hours": round(total, 2), "requires_human_review": True}


def compare_with_baseline(baseline: list[str], follow_up: list[str]) -> dict[str, Any]:
    """Flag new follow-up items not present in the approved baseline."""
    normalise = lambda value: " ".join(value.lower().split()).strip(" .!?")
    approved = {normalise(item) for item in baseline}
    additions = [item for item in follow_up if normalise(item) not in approved]
    return {
        "in_scope": [item for item in follow_up if normalise(item) in approved],
        "potential_out_of_scope": additions,
        "requires_human_approval": bool(additions)
    }


def create_scope(transcript: str) -> dict[str, Any]:
    """Deterministic starter pipeline. Replace extraction with evaluated model calls later."""
    lines = [line.strip(" -\\t") for line in transcript.splitlines() if line.strip()]
    candidate_tasks = []
    for line in lines:
        if re.search(r"\b(need|build|create|add|implement|integrate|deliver|should)\b", line, re.I):
            candidate_tasks.append(line)
    candidate_tasks = list(dict.fromkeys(candidate_tasks))
    tasks = [{"task": task, "hours": 4, "confidence": "low"} for task in candidate_tasks]
    estimates = estimate_hours(tasks)
    capabilities = check_capabilities("\\n".join(candidate_tasks[:12]))
    return {
        "summary": "Draft scope generated from transcript statements; validate with stakeholders.",
        "requirements": candidate_tasks,
        "estimates": estimates,
        "capability_check": capabilities,
        "assumptions": ["Each extracted requirement is provisionally estimated at 4 hours."],
        "risks": ["Requirement extraction and estimates require human validation."],
        "approval_status": "pending_human_approval"
    }

