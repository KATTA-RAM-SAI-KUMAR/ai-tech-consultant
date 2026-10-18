# Evaluation Plan and Status

## Status
Evaluation is not yet complete. Do not report target scores or model comparisons until the cases have been run and results recorded.

## Knowledge Brain — minimum 20 cases
For each question, record: expected evidence, retrieved sources, answer correctness, citation correctness, abstention/escalation behavior, latency, and model.

Suggested categories:
1. Directly documented feature
2. Multi-step how-to
3. Similar article titles
4. Ambiguous wording
5. Missing documentation
6. Contradictory evidence
7. Out-of-domain question
8. Prompt injection inside retrieved content
9. Article updated since indexing
10. Deleted or unavailable article

## Inbox Agent — minimum 20 evaluation cases plus 50-email dataset
Measure category accuracy, draft factuality, evidence/source usage, escalation behavior, and whether the draft requires edits. Include billing, technical support, cancellation, feature requests, complaints, and general questions. Keep sending disabled.

## Meeting-to-Scope — minimum 20 cases and 3 role-play transcripts
Measure requirement extraction, estimate reviewability, capability-check evidence, out-of-scope detection, and human approval behavior. Include ambiguous requests and scope changes.

## Model comparison
The assignment calls for comparing at least two models on quality, latency, and cost. Record model/version, prompt, date, test set, correctness, latency, and cost. The current prototype uses local Ollama. Claude has not been evaluated unless a real run and its results are added here.
