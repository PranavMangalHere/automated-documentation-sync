# Phase 6 — Sample User Story & End-to-End Test

## Goal

Validate the entire pipeline by running it against a concrete, well-defined Python project user story.

This phase produces the first real output from all 9 agents and confirms that the orchestrator drives them correctly from the user story through to a GitHub Pull Request.

---

## Prerequisites

* All previous phases complete (Phases 1–5)
* Git repository initialized with a remote on GitHub
* `gh` CLI authenticated
* `pytest` available in the environment
* GitHub Copilot available in the project

Verify GitHub CLI authentication:

```bash
gh auth status
```

Verify pytest:

```bash
pytest --version
```

---

# Step 6.1 — Create the Sample User Story

Create:

```text
user-stories/user-story-template.md
```

The user story should be:

* Simple enough to implement in a single session
* Complex enough to exercise all pipeline stages meaningfully
* Self-contained
* Free from external APIs or services

### Recommended Story — Task List CLI Tool

```markdown
# User Story: Task List CLI

**As a** person managing daily tasks,

**I want** a command-line tool that lets me add, list, and complete tasks,

**So that** I can keep a simple local task list without an external service.

## Details

- The tool is invoked from the command line as `python -m task_list`.
- `add` accepts a non-empty description and prints the created task ID:
  `python -m task_list add "Buy groceries"`.
- `list` prints every task with its ID, status (`pending` or `complete`), and description.
- `complete` accepts a task ID, marks the matching pending task as complete, and prints a confirmation.
- Tasks persist in `.task-list.json` in the current working directory.
- A missing storage file is treated as an empty task list.
- An empty description, unknown task ID, or invalid command prints a clear error to stderr and exits with code 1.
- An empty task list prints `No tasks found` and exits with code 0.
- The tool uses only the Python standard library.

## Acceptance Criteria

1. Given a non-empty description, `add` stores a pending task and prints its ID.
2. Given one or more stored tasks, `list` prints each task's ID, status, and description.
3. Given an existing pending task ID, `complete` marks the task as complete and prints a confirmation.
4. Given an unknown task ID, `complete` prints a clear error to stderr and exits with code 1.
5. Given an empty task list, `list` prints `No tasks found` and exits with code 0.
6. Tasks added in one command are available to later `list` and `complete` commands.
7. The CLI help command exits with code 0 and describes the available commands.
```

---

# Step 6.2 — Prepare the Environment

Before running the pipeline, verify the environment.

### Confirm GitHub CLI authentication

```bash
gh auth status
```

### Confirm pytest is available

```bash
pytest --version
```

### Confirm the Git remote

```bash
git remote -v
```

If no remote exists, add one:

```bash
git remote add origin https://github.com/<your-username>/automated-documentation-sync.git
```

Then push the main branch:

```bash
git push -u origin main
```

---

# Step 6.3 — Run the Pipeline

Open the GitHub Copilot agent environment in the project repository and invoke the orchestrator:

```text
@orchestrator process user-stories/user-story-template.md
```

The user should invoke **only the orchestrator**. The orchestrator is responsible for coordinating all specialist agents.

---

## Expected Interaction Flow

### Step 1 — Requirements (L1)

* Orchestrator invokes the Requirements agent.
* Requirements agent reads the user story.
* Agent identifies ambiguities and asks clarifying questions.
* You provide the required decisions.
* Agent creates:

```text
docs/requirements.md
```

* Orchestrator validates the artifact.
* Pipeline proceeds after the L1 requirement gate is satisfied.

Example clarification:

```text
Use only the Python standard library and store tasks in `.task-list.json`.
```

or:

```text
Output format should be plain text, not JSON.
```

---

### Step 2 — Architecture (L1)

* Orchestrator invokes the Architecture agent.
* Architecture agent reads `docs/requirements.md`.
* Agent proposes the Python module structure.
* You approve or request adjustments.
* Agent creates:

```text
docs/architecture.md
```

Example decision:

```text
Use argparse instead of click.
```

* Orchestrator validates the artifact.
* Pipeline proceeds after the L1 architecture gate is satisfied.

---

### Step 3 — Design Review (L2)

* Orchestrator invokes the Design Review agent.
* Agent reviews the architecture.
* Agent creates:

```text
docs/design-review.md
```

* Orchestrator displays the review.
* You review the risks, decisions, and required changes.
* You type:

```text
y
```

to continue.

---

### Step 4 — Implementation Planning (L2)

* Orchestrator invokes the Implementation Planner.
* Agent reads the architecture and design review.
* Agent creates:

```text
docs/impl-plan.md
```

* Orchestrator displays the implementation task table.
* You type:

```text
y
```

to continue.

---

### Step 5 — Implementation (L2)

The Implementation agent:

* Reads `docs/impl-plan.md`
* Creates the Python source files
* Creates unit tests
* Creates integration tests
* Runs the test suite
* Reports the results

Expected structure may include:

```text
src/
└── task_list/
    ├── __init__.py
    ├── cli.py
    └── storage.py

tests/
├── unit/
│   └── test_storage.py
└── integration/
    └── test_cli.py
```

The orchestrator shows:

* Files created
* Test results
* Implementation summary

You type:

```text
y
```

to continue.

---

### Step 6 — Documentation Sync (L2)

* Orchestrator invokes the Documentation Sync agent.
* Agent scans the implementation.
* Agent identifies documentation that needs updating.
* Agent updates the relevant documentation.
* Agent creates or updates:

```text
output/reports/doc-sync-report.md
```

* Orchestrator displays the sync report.
* You type:

```text
y
```

to continue.

---

### Step 7 — Code Review (L2)

* Orchestrator invokes the Code Review agent.
* Agent reviews the Python implementation against the requirements.
* Agent checks code quality, design, tests, and potential issues.
* Agent creates:

```text
output/reports/code-review.md
```

* Orchestrator displays the review.
* You type:

```text
y
```

to continue.

If issues are found, you may type:

```text
n
```

to pause the pipeline and address them.

---

### Step 8 — Verification (L2)

* Orchestrator invokes the Verification agent.
* Agent runs the complete test suite.
* Agent performs the required verification checks.
* Agent creates:

```text
output/test-results/results.md
```

* Orchestrator displays the results.
* The verification result must contain a final PASS/FAIL verdict.

You type:

```text
y
```

to continue to the PR stage.

---

### Step 9 — Pull Request (L3)

* Orchestrator invokes the PR agent.
* PR agent prepares the complete PR description.
* Orchestrator displays the PR draft.
* You explicitly approve the PR creation.

You type:

```text
y
```

Only after explicit confirmation does the PR agent execute:

```bash
gh pr create
```

The orchestrator then displays the generated GitHub Pull Request URL.

---

# Step 6.4 — Validate Artifacts

After the pipeline completes, validate each artifact.

## `docs/` Artifacts

* [ ] `docs/requirements.md` contains:

  * Functional Requirements
  * Non-Functional Requirements
  * Acceptance Criteria

* [ ] `docs/architecture.md` contains:

  * Component Diagram
  * Technology Choices
  * Data Flow

* [ ] `docs/design-review.md` contains:

  * Risk Table
  * Design Decisions
  * Required Changes

* [ ] `docs/impl-plan.md` contains:

  * Ordered task table
  * Dependencies

* [ ] `docs/changelog.md` contains:

  * Agent/pipeline activity
  * Timestamps
  * Pipeline progression

---

## `src/` Artifacts

* [ ] At least 3 Python source files exist in `src/`
* [ ] Source files contain appropriate type hints
* [ ] No hardcoded secrets or credentials exist
* [ ] The CLI help command works:

```bash
python -m task_list --help
```

---

## `tests/` Artifacts

* [ ] Unit tests exist in:

```text
tests/unit/
```

* [ ] Integration tests exist in:

```text
tests/integration/
```

* [ ] Test suite passes:

```bash
pytest tests/ -v
```

Expected result:

```text
0 failures
```

---

## `output/` Artifacts

* [ ] `output/reports/doc-sync-report.md` exists
* [ ] `output/reports/code-review.md` contains an Overall Recommendation
* [ ] `output/test-results/results.md` contains:

```text
Final Verdict: PASS
```

---

## GitHub

* [ ] Pull Request exists

* [ ] PR description contains:

  * Summary
  * Changes Made
  * Test Evidence
  * Known Limitations
  * Reviewer Checklist

* [ ] PR description contains the required attribution line

---

# Step 6.5 — Final Commit

If any pipeline outputs were not automatically committed, commit them manually:

```bash
git add docs/ src/ tests/ output/
```

Then:

```bash
git commit -m "feat: run agentic pipeline on task list user story"
```

Push the changes:

```bash
git push
```

---

# Deliverables Checklist

* [ ] `user-stories/user-story-template.md` created
* [ ] Task List user story included
* [ ] Full pipeline run completed
* [ ] All 9 specialist agents executed through the orchestrator
* [ ] L1/L2/L3 interaction points validated
* [ ] All required artifacts validated
* [ ] `pytest tests/ -v` passes
* [ ] GitHub Pull Request created
* [ ] All artifacts committed

---

# Troubleshooting

| Problem                                  | Likely Cause                                             | Fix                                                 |
| ---------------------------------------- | -------------------------------------------------------- | --------------------------------------------------- |
| Gate fails on `docs/requirements.md`     | Requirements agent did not produce the required artifact | Resume the orchestrator from the requirements stage |
| `gh pr create` fails                     | GitHub CLI is not authenticated or remote is missing     | Run `gh auth login` and verify `git remote -v`      |
| `pytest` fails                           | Implementation does not satisfy one or more tests        | Review the failing test and implementation          |
| Hook script permission denied            | Script is not executable                                 | Run `chmod +x .github/hooks/scripts/*.sh`           |
| Coverage is below the required threshold | Tests are incomplete                                     | Add the required tests and rerun verification       |
| PR creation is blocked                   | L3 approval was not provided                             | Review the PR draft and explicitly approve it       |

---

# Success Definition

The pipeline is considered complete when:

1. A user story placed inside `user-stories/` can be processed by invoking the orchestrator once.

2. All 9 specialist agents run without the user directly invoking individual agents.

3. The orchestrator correctly controls the complete sequence:

```text
User Story
    ↓
Orchestrator
    ↓
Requirements
    ↓
Architecture
    ↓
Design Review
    ↓
Implementation Planning
    ↓
Implementation
    ↓
Documentation Sync
    ↓
Code Review
    ↓
Verification
    ↓
PR
```

4. Human interaction is limited to:

   * Answering L1 clarification questions
   * Approving L2 stages
   * Confirming the L3 Pull Request

5. The final result is a tested Python implementation with the required documentation, verification artifacts, and a GitHub Pull Request.
