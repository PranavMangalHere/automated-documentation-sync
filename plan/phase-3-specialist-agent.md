# Phase 3 — Specialist Agents

## Goal

Create 9 specialist GitHub Copilot agent files under `.github/agents/`. Each agent has a single, well-defined responsibility in the pipeline. Agents read from documented input files and write to documented output files. The orchestrator (Phase 4) is the only caller — agents never invoke each other directly.

---

## Prerequisites

* Phase 1 complete (directories exist)
* Phase 2 complete (skills exist for agents to reference)

---

## What Is a GitHub Copilot Agent File?

A `.github/agents/*.agent.md` file defines a specialized GitHub Copilot agent. It contains YAML frontmatter and agent instructions that define the agent's role, purpose, available tools, and behavior.

The orchestrator uses these specialist agents as the individual stages of the SDLC pipeline.

**Standard frontmatter structure:**

```yaml
---
name: <agent-name>
description: <one-line description used by the orchestrator>
tools:
  - read
  - edit
  - search
  - execute
---
```

The exact tools available to an agent should be limited to what that agent needs to perform its responsibility.

---

## Agents to Create

### Agent 1 — `requirements.agent.md`

**Interaction Level**: L1 (Deep Interactive — can ask clarifying questions)

**Input**: User story file path (passed by orchestrator)

**Output**: `docs/requirements.md`

**Agent instructions must require the agent to:**

* Read the user story file in full before doing anything else
* Use the `requirement-analysis` skill to structure its work
* Ask all clarifying questions in a single numbered list — never one at a time
* Wait for user answers, then produce the final `docs/requirements.md`
* Allow maximum 2 rounds of clarification before writing the document
* Confirm with the user that `requirements.md` is complete before returning to the orchestrator
* Never proceed to architecture — that is the orchestrator's job

**Tools needed**: Read, Edit

**Output file format**: See the `requirement-analysis` skill for the exact structure.

---

### Agent 2 — `architecture.agent.md`

**Interaction Level**: L1 (Deep Interactive — can ask clarifying questions about design choices)

**Input**: `docs/requirements.md`

**Output**: `docs/architecture.md`

**Agent instructions must require the agent to:**

* Read `docs/requirements.md` fully before proposing anything
* Use the `architecture-design` skill to structure its work
* Propose a complete architecture first, then ask if the user has preferences or constraints to adjust
* If a requirement is ambiguous for design purposes, ask before assuming
* Write `docs/architecture.md` only after the user approves the design
* Never write source code — only the architecture document
* Confirm with the user that `architecture.md` is complete before returning

**Tools needed**: Read, Edit

---

### Agent 3 — `design-review.agent.md`

**Interaction Level**: L2 (Run autonomously, output shown by orchestrator, user approves before next step)

**Input**: `docs/architecture.md`

**Output**: `docs/design-review.md`

**Agent instructions must require the agent to:**

* Read `docs/architecture.md` as a senior technical reviewer (not the original author)
* Evaluate against these risk categories:

  * Scalability risks
  * Security gaps
  * Missing error handling strategy
  * Over-engineering or under-engineering
  * Unaddressed non-functional requirements
  * Missing component interfaces
* Write `docs/design-review.md` with:

  * Summary
  * Risk Table (Risk | Severity | Recommendation)
  * Design Decisions Confirmed
  * Required Changes Before Implementation
* If Required Changes are non-empty, flag this clearly — the orchestrator will surface it to the user
* Never modify `docs/architecture.md` itself

**Tools needed**: Read, Edit

---

### Agent 4 — `implementation-planner.agent.md`

**Interaction Level**: L2

**Input**: `docs/architecture.md` + `docs/design-review.md`

**Output**: `docs/impl-plan.md`

**Agent instructions must require the agent to:**

* Read both input files before planning
* Use the `implementation-planning` skill to structure the task breakdown
* Produce an ordered, dependency-aware task list for a Python project
* Each task must:

  * Be independently testable
  * Have a clear definition of done
  * Reference the file(s) it creates or modifies
* Pair each implementation task with a corresponding test task
* Flag any task that is blocked on an external dependency
* Write `docs/impl-plan.md` with the full task table and dependency graph
* Never write source code

**Tools needed**: Read, Edit

---

### Agent 5 — `implementation.agent.md`

**Interaction Level**: L2

**Input**: `docs/impl-plan.md` (+ `docs/requirements.md` and `docs/architecture.md` for context)

**Output**: `src/**/*.py` + `tests/**/*.py`

**Agent instructions must require the agent to:**

* Read `docs/impl-plan.md` and execute tasks in the dependency order defined there
* Read `docs/requirements.md` to stay anchored to acceptance criteria
* Write Python source files to `src/` following the architecture
* Write corresponding test files to `tests/unit/` and `tests/integration/`
* Follow these Python conventions strictly:

  * Type hints on all function signatures
  * No bare `except:` — always catch specific exceptions
  * No mutable default arguments
  * No secrets or credentials hardcoded
  * Functions ≤ 30 lines where possible
* After writing all files, run `pytest` to confirm tests pass before returning
* Report to orchestrator:

  * Files created
  * Test results summary

**Tools needed**: Read, Edit, Search, Execute

---

### Agent 6 — `documentation-sync.agent.md`

**Interaction Level**: L2

**Input**: `src/` directory + existing `docs/` files

**Output**: Updated `docs/*.md` files + sync report

**Agent instructions must require the agent to:**

* Use the `documentation-sync` skill to guide its work
* Scan all `.py` files in `src/` and compare against what `docs/architecture.md` and `docs/requirements.md` describe
* Identify gaps:

  * New components not documented
  * Removed items still referenced
  * Changed interfaces
* Update only the affected sections — do not rewrite accurate content
* Write a short sync report to `output/reports/doc-sync-report.md` listing all changes made
* If a discrepancy suggests the implementation deviated from the architecture, flag it clearly

**Tools needed**: Read, Edit, Search

---

### Agent 7 — `code-review.agent.md`

**Interaction Level**: L2

**Input**: `src/**/*.py` + `tests/**/*.py` + `docs/requirements.md`

**Output**: `output/reports/code-review.md`

**Agent instructions must require the agent to:**

* Use the `code-review` skill checklist for all 8 review areas
* Read every `.py` file in `src/` and `tests/`
* Cross-reference findings against `docs/requirements.md` — only flag deviations from spec, not style preferences
* Assign severity:

  * Critical — breaks functionality or security
  * Major — significant quality issue
  * Minor — style or clarity issue
* Write `output/reports/code-review.md` with the full finding table
* End with **Overall Recommendation: Approve / Request Changes**
* If any Critical finding exists, set recommendation to **Request Changes** automatically

**Tools needed**: Read, Edit, Search

---

### Agent 8 — `verification.agent.md`

**Interaction Level**: L2

**Input**: `src/` + `tests/` + `docs/requirements.md`

**Output**: `output/test-results/results.md`

**Agent instructions must require the agent to:**

* Use the `verification` skill to structure the test run
* Execute:

  * `pytest tests/unit/ -v`
  * `pytest tests/integration/ -v`
  * `pytest --cov=src --cov-report=term-missing`
* Map each acceptance criterion from `docs/requirements.md` to the test(s) that cover it
* Flag any criterion with zero test coverage as a gap
* Write `output/test-results/results.md` with:

  * Run summary
  * Coverage report
  * Criteria coverage table
  * Gaps
  * Final PASS/FAIL verdict
* Pass criteria:

  * All tests pass
  * Coverage ≥ 80%
  * No Critical code review findings still open
* If verdict is FAIL, list exactly what must be fixed before PR can be created

**Tools needed**: Read, Edit, Execute, Search

---

### Agent 9 — `pr.agent.md`

**Interaction Level**: L3 (Explicit Approve — draft shown, PR created only after user confirms)

**Input**: All `docs/*.md` + `output/reports/` + `output/test-results/results.md`

**Output**: GitHub Pull Request URL

**Agent instructions must require the agent to:**

* Read all artifact files to construct the PR description
* Generate a complete PR draft with all required sections:

  1. **Summary** — 2–3 sentence overview of what was built and why
  2. **Changes Made** — bulleted list of all files added/modified with reason
  3. **Test Evidence** — key lines from `output/test-results/results.md`
  4. **Known Limitations** — anything marked "Not Found", out of scope, or flagged as a gap
  5. **Reviewer Checklist** — tick-list the reviewer must complete before approving
* Present the full draft to the orchestrator **without creating the PR yet**
* Only create the PR after receiving explicit confirmation from the orchestrator, which relays it from the user
* Use GitHub MCP to perform PR creation: accept an MCP action `create_pr` (payload: title, body, head_branch, base_branch, draft, reviewers, labels) and return a standardized JSON response on success, for example: `{ "status": "created", "pr_number": 42, "pr_url": "https://github.com/owner/repo/pull/42" }`.
* If MCP is unavailable, the agent should include a clear, documented CLI fallback (present the `gh pr create` command the user can run manually) but prefer MCP as the primary mechanism.

**Tools needed**: Read, Execute, Search

---

## Deliverables Checklist

* [ ] `.github/agents/requirements.agent.md`
* [ ] `.github/agents/architecture.agent.md`
* [ ] `.github/agents/design-review.agent.md`
* [ ] `.github/agents/implementation-planner.agent.md`
* [ ] `.github/agents/implementation.agent.md`
* [ ] `.github/agents/documentation-sync.agent.md`
* [ ] `.github/agents/code-review.agent.md`
* [ ] `.github/agents/verification.agent.md`
* [ ] `.github/agents/pr.agent.md`
* [ ] All 9 files committed

---

## Verification

For each agent file:

1. Confirm frontmatter is valid YAML with `name`, `description`, and `tools`.
2. Confirm the agent instructions reference the correct input files and output files.
3. Confirm the interaction level is correctly described:

   * L1 agents must mention Q&A iteration.
   * L2 agents must run and return their results for orchestrator approval.
   * L3 agent must mention draft-first and create-only-on-confirm.
4. Confirm no agent attempts to call another agent — only the orchestrator coordinates the pipeline.
5. Confirm each agent references the appropriate skill from Phase 2 where required.
6. Confirm the 9 agents preserve the exact pipeline order defined in the project plan.
