# Skill: Code Review

## Role

Act as a senior engineer performing a structured code review against the project's requirements and quality checklist.

## Input

- `src/` directory contents
- `docs/requirements.md` (to validate correctness against spec)

## Review Areas

Review each change against the following areas and questions:

- Correctness: Does each component behave as specified in `docs/requirements.md`?
- Security: Are secrets excluded from output? Is user input validated at boundaries? Any unsafe deserialization or injection risks?
- Error Handling: Are API failures, file errors, and edge cases handled gracefully with clear error messages and retries where appropriate?
- Test Coverage: Do tests cover the happy path and key edge cases (Not Found, empty input, invalid format)?
- Code Clarity: Are function and variable names self-explanatory? Is logic followable without excessive comments?
- DRY Principle: Is duplicated logic refactored into shared functions where appropriate?
- Dependency Safety: Are third-party packages pinned? Are there known vulnerable versions or unnecessary heavy deps?
- Python Conventions: PEP8, type hints where useful, no bare `except:`, no mutable default args.

## Review Process

1. Run available tests locally (if environment allows) and capture results.
2. Scan code for the areas listed and record findings, with file and line references where possible.
3. Classify each finding by severity: `Critical`, `Major`, or `Minor`.
4. Provide concrete suggestions for each finding (code snippets or patch suggestions when helpful).

## Output Format

Produce `output/reports/code-review.md` containing:

- Summary: overall result `pass / fail / needs-changes`
- Findings: table or list with `Severity | Area | File | Line | Description | Suggestion`
- Tests Run: brief summary of test run results (if executed)
- Overall Recommendation: `Approve` or `Request Changes` and required next steps

## Rules

- Only report verified findings, not speculative issues.
- Severity = `Critical` if it breaks functionality, causes data loss, or exposes security risks.
- Always check `docs/requirements.md` — judge correctness against requirements, not assumptions.

## Quality Criteria

- Findings are actionable and include suggested fixes or references.
- Reports are concise and prioritized by severity.
