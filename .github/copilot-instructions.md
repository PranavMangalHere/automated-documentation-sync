# Project Overview

Automated Documentation Sync is an agentic SDLC pipeline driven by GitHub Copilot. It accepts a Python project user story and runs a coordinated set of Copilot custom agents to produce requirements, architecture, implementation, documentation updates, automated tests, and a PR — all gated by human approvals according to the project interaction model.

## How to Run the Pipeline

Invoke the orchestrator from a Copilot-enabled environment by addressing it with a user story path:

@orchestrator process user-stories/<filename>.md

The orchestrator will drive each specialist agent in sequence and prompt for approvals where required.

## Pipeline Phases

1. Requirements — elicit and record requirements into `docs/requirements.md`.
2. Architecture — propose a design and produce `docs/architecture.md`.
3. Design Review — L2 review and risk analysis in `docs/design-review.md`.
4. Implementation Planner — ordered task breakdown in `docs/impl-plan.md`.
5. Implementation — generate `src/` and `tests/` artifacts.
6. Documentation Sync — keep `docs/` in sync with code changes.
7. Code Review — static review output to `output/reports/`.
8. Verification — run tests and write `output/test-results/results.md`.
9. PR — draft and create the GitHub pull request after explicit approval.

## Interaction Levels

L1 — Deep Interactive: Agents may ask clarifying questions and iterate until approved.

L2 — Run + Approve: Agents run autonomously, present results, and wait for a simple "y/n" to continue.

L3 — Explicit Approve: The PR agent shows the full PR draft and only creates the PR after explicit user confirmation.

## File Conventions

- User stories live in `user-stories/` and should be named using kebab-case with a `.md` extension (e.g., `user-story-1.md`).
- Generated documentation is stored under `docs/`.
- Source code goes under `src/`; tests under `tests/unit/` and `tests/integration/`.
- Tool outputs (reports, test results) are written to `output/reports/` and `output/test-results/` respectively.

## Do Not

- Invoke specialist agents directly when the orchestrator should coordinate them.
- Skip gating checks that verify outputs exist and are non-empty before proceeding.
- Skip required pipeline stages.
- Modify artifacts belonging to another stage without following the orchestrator's pipeline.
- Create the PR without explicit user confirmation.
