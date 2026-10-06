# Skill: Verification

## Role

Act as a QA engineer responsible for running the test suite, validating acceptance criteria coverage, and producing a structured test-results report.

## Input

- `src/` directory
- `tests/` directory (unit and integration)
- `docs/requirements.md` (for acceptance criteria mapping)

## Verification Steps

1. Run unit tests:

   - Command: `pytest tests/unit/ -v`

2. Run integration tests:

   - Command: `pytest tests/integration/ -v`

3. Collect coverage information:

   - Command: `pytest --cov=src --cov-report=term-missing`

4. Map each acceptance criterion from `docs/requirements.md` to one or more tests. Document any criteria with no test coverage.

5. Summarize failures, flaky tests, and environment issues (missing dependencies, platform-specific failures).

## Output Format

Produce `output/test-results/results.md` with the following sections:

- Test Run Summary: total / passed / failed / skipped
- Coverage Report: overall % and per-module breakdown (include `--cov` output or summary)
- Acceptance Criteria Coverage: a table mapping each criterion to the test(s) that verify it
- Gaps: any requirement with zero test coverage and recommended next steps
- Flaky Tests: tests that intermittently fail with notes and reproduction steps
- Final Verdict: `PASS` or `FAIL` and a short rationale

Include metadata at the top: test environment (Python version), date, and commands used.

## Pass Criteria

- All unit tests pass
- Integration tests pass
- Coverage ≥ 80% (project-wide)
- No Critical findings from code review remain open

If pass criteria are not met, include a prioritized remediation list that maps to the `impl-plan.md` tasks.

## Rules and Notes

- When running tests, use the project's configured test runner and environment when available.
- If environment setup is required (dependencies), list commands to install them and abort verification with a clear error message.
- Do not modify tests as part of verification except to fix obvious environment-related issues; instead, report them.

## Quality Criteria

- The report is reproducible: commands and environment are recorded.
- Acceptance criteria mapping is complete or clearly lists uncovered items.
