# Design

## Architecture
- Task 1 exposes retrieval and grounded question answering over support documentation.
- Task 2 accepts an email, assigns a category, queries Task 1, and returns a draft with source links for human review.
- Task 3 turns transcript statements into candidate requirements, provides transparent provisional effort estimates, calls Task 1 for capability evidence, and compares follow-up items with an approved baseline.

## Trust boundaries
- External support documentation is untrusted input.
- Retrieved text is evidence, not instructions to the agent.
- The model must not be allowed to approve work, send email, or alter a scope baseline.
- Human approval is required before external actions.
- If retrieval fails or evidence is insufficient, the system must disclose that limitation.

## Known limitations
- The inbox classifier currently uses keyword rules.
- Email draft wording is a template, not a fully evaluated language model output.
- Meeting requirement extraction is heuristic and may miss or misinterpret requirements.
- Hours are provisional placeholders until replaced with reviewed estimates.
- Removed pages, crawl coverage, and model evaluation require additional validation.
