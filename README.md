# Automated Documentation Sync

What This Is

Automated Documentation Sync is a GitHub Copilot-native agentic SDLC pipeline that takes a Python project user story and drives it through requirements, design, implementation, documentation sync, testing, and a PR — coordinated by an orchestrator agent.

Quick Start

1. Clone the repository.
2. Add a user story to `user-stories/` (use kebab-case and `.md`).
3. Invoke the orchestrator: `@orchestrator process user-stories/<your-story>.md`.
4. Follow Copilot prompts and approve steps when requested.

Pipeline Architecture

user-stories -> orchestrator -> requirements -> architecture -> design-review -> impl-planner -> implementation -> doc-sync -> code-review -> verification -> pr

Folder Structure

- `.github/` — agents, skills, prompts, and pipeline instructions.
- `user-stories/` — story files that drive the pipeline.
- `docs/` — generated documentation artifacts.
- `src/` — generated source code.
- `tests/` — generated tests.
- `output/` — reports and test results.
- `pyproject.toml`, `.gitignore` — project metadata and ignores.

Agent Reference

- Orchestrator — coordinates the pipeline and enforces gates (L2/L3 approvals).
- Requirements (L1) — elicits requirements.
- Architecture (L1) — proposes system design.
- Design Review (L2) — reviews architecture.
- Implementation Planner (L2) — creates implementation task lists.
- Implementation (L2) — writes code and tests.
- Documentation Sync (L2) — keeps docs updated with code.
- Code Review (L2) — generates review reports.
- Verification (L2) — runs tests and records results.
- PR (L3) — prepares PR and creates it only after explicit approval.

Requirements

- GitHub Copilot installed and enabled in VS Code.
- Git and Python >= 3.11.

Contributing

To add a new agent or skill, create a new file under `.github/agents/` or `.github/skills/` and update `.github/copilot-instructions.md` to describe its role and interaction level.
