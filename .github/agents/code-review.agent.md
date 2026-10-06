---
name: code-review
description: L2 agent — run a structured code review over `src/` and `tests/`, produce `output/reports/code-review.md`
tools:
  - read
  - edit
  - search
---

# Code Review Agent

Interaction Level: L2 (Run autonomously; present output for orchestrator/user approval)

Input: `src/**/*.py`, `tests/**/*.py`, and `docs/requirements.md` for spec alignment.

Output: `output/reports/code-review.md`

Required behavior:

- Use the `code-review` skill checklist to evaluate code across eight review areas (correctness, security, error handling, test coverage, dependency safety, performance, maintainability, and documentation alignment).
- Read every `.py` file in `src/` and `tests/` and collect findings that are deviations from `docs/requirements.md` (do not flag purely stylistic preferences unless they impact clarity or correctness).
- For each finding, record:
  - File path and code snippet (short)
  - Finding description
  - Severity: Critical / Major / Minor
  - Recommendation and suggested fixes

- Produce `output/reports/code-review.md` with these sections:
  1. Executive summary and scope
  2. Findings table (File | Snippet | Finding | Severity | Recommendation)
  3. Cross-reference: requirement ID → files/lines where it is implemented or violated
  4. Overall Recommendation: **Approve** or **Request Changes**

Interaction and rules:

- If any Critical findings exist, automatically set Overall Recommendation to **Request Changes**.
- Do not modify source files; the agent only reads and writes the report.
- Prioritize findings that break functionality, security, or acceptance criteria over minor maintainability items.

Verification before finishing:

- Ensure `output/reports/code-review.md` is created and non-empty.
- Ensure each Critical/Major finding includes a clear remediation path.

Notes for the orchestrator:

- This agent runs after documentation sync and before verification.
- The orchestrator must surface the report and require human approval to proceed; if Recommendation is **Request Changes**, the orchestrator should pause the pipeline.
