# AI Development Log

## Initial implementation
- Reused the existing Task 1 FastAPI retrieval service and PostgreSQL/pgvector database.
- Added a local Ollama generation path using `llama3.2:3b`.
- Added a TypeScript Inbox Agent service with keyword-based classification, Knowledge Brain lookup, and human-review drafts.
- Added a Python Meeting-to-Scope API with transcript requirement heuristics, provisional estimates, Knowledge Brain capability checks, and baseline comparison.
- Added an initial design document and an evaluation plan.

## Important limitations
- No Claude model comparison has been performed yet.
- The current meeting estimator uses a placeholder 4-hour estimate per extracted item.
- The inbox draft is template-based and requires human review.
- Evaluation counts and results must be added only after actual tests are executed.
