# Phase 5 — Hooks

## Goal

Configure GitHub Copilot hooks to add automated behaviors around the pipeline:

* Log agent invocations
* Validate output files
* Print a pipeline summary when the session ends

Hooks run outside the agent's normal reasoning context. They are external commands executed by the GitHub Copilot runtime.

---

## Prerequisites

* Phase 1 complete (`.github/` directory exists)
* Phase 3 complete (agent files exist)
* Phase 4 complete (orchestrator exists)

---

## What Are GitHub Copilot Hooks?

GitHub Copilot hooks allow external commands to execute at specific points in the agent lifecycle.

Repository-level hooks are configured under:

```text
.github/hooks/
```

Hook configuration files use:

```json
{
  "version": 1,
  "hooks": {}
}
```

Relevant hook types for this project are:

| Hook Type       | Fires When               |
| --------------- | ------------------------ |
| `subagentStart` | A subagent starts        |
| `subagentStop`  | A subagent completes     |
| `postToolUse`   | A tool completes         |
| `sessionEnd`    | The Copilot session ends |

For this project, hooks are **informational and validation-oriented**. They must not replace the orchestrator's pipeline gates.

---

# Hooks to Configure

## Hook 1 — Agent Invocation Logger

**Hook Type:** `subagentStart`

### Purpose

Log every specialist-agent invocation to:

```text
docs/changelog.md
```

### Trigger

```text
subagentStart
```

### Script

Create:

```text
.github/hooks/scripts/log-agent-invocation.sh
```

```bash
#!/bin/bash

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "" >> docs/changelog.md
echo "### $TIMESTAMP — Subagent started" >> docs/changelog.md
```

### Notes

* Runs when a subagent starts.
* Adds a timestamped entry to `docs/changelog.md`.
* The hook is informational only.
* It must not block the pipeline.

---

# Hook 2 — Output File Validator

**Hook Type:** `postToolUse`

### Purpose

After a tool completes, validate relevant output files and warn when an expected file is empty.

### Trigger

```text
postToolUse
```

The hook should inspect the Copilot hook input payload and determine whether the completed tool operation affected a relevant file.

### Script

Create:

```text
.github/hooks/scripts/validate-output-file.sh
```

```bash
#!/bin/bash

# The Copilot hook payload should be read from stdin.
INPUT=$(cat)

# Output the received event for diagnostic purposes.
echo "postToolUse event received." >&2

# File extraction should be implemented according to
# the tool arguments provided in the Copilot hook payload.

echo "Output validation hook executed." >&2
```

### Validation Rules

The implementation should validate files under:

```text
docs/
output/
```

For a relevant file:

* Check whether the file exists.
* Check whether the file is non-empty.
* Report the result.
* Do not block the pipeline.

Example expected output:

```text
OK: docs/requirements.md contains content
```

or:

```text
WARNING: docs/requirements.md was written but is empty.
```

### Notes

* `postToolUse` receives information about the completed tool operation.
* The implementation should parse the hook payload to identify the affected file.
* The hook must not assume undocumented environment variables.
* The orchestrator remains responsible for deciding whether the pipeline can continue.

---

# Hook 3 — Pipeline Summary Printer

**Hook Type:** `sessionEnd`

### Purpose

When the Copilot session ends, print a summary of the artifacts produced by the pipeline.

### Trigger

```text
sessionEnd
```

### Script

Create:

```text
.github/hooks/scripts/print-pipeline-summary.sh
```

```bash
#!/bin/bash

echo ""
echo "========================================"
echo "  PIPELINE RUN SUMMARY"
echo "========================================"

check_file() {
  if [ -s "$1" ]; then
    echo "  [OK]  $1"
  else
    echo "  [--]  $1 (not produced)"
  fi
}

check_file "docs/requirements.md"
check_file "docs/architecture.md"
check_file "docs/design-review.md"
check_file "docs/impl-plan.md"
check_file "output/reports/doc-sync-report.md"
check_file "output/reports/code-review.md"
check_file "output/test-results/results.md"

SRC_COUNT=$(find src/ -name "*.py" 2>/dev/null | wc -l)
TEST_COUNT=$(find tests/ -name "*.py" 2>/dev/null | wc -l)

echo "  [SRC] $SRC_COUNT Python source files in src/"
echo "  [TST] $TEST_COUNT Python test files in tests/"
echo ""

if [ -s "output/test-results/results.md" ]; then
  VERDICT=$(grep -i "Final Verdict" output/test-results/results.md | tail -1)
  echo "  Verification: $VERDICT"
fi

echo "========================================"
```

### Notes

* Runs when the Copilot session ends.
* Does not modify project files.
* Reports which pipeline artifacts were produced.
* Reports source and test file counts.
* Reports the verification verdict when available.
* Does not block or alter the pipeline.

---

# `.github/hooks/pipeline-hooks.json`

Create:

```text
.github/hooks/pipeline-hooks.json
```

```json
{
  "version": 1,
  "hooks": {
    "subagentStart": [
      {
        "type": "command",
        "bash": "bash .github/hooks/scripts/log-agent-invocation.sh"
      }
    ],
    "postToolUse": [
      {
        "type": "command",
        "bash": "bash .github/hooks/scripts/validate-output-file.sh"
      }
    ],
    "sessionEnd": [
      {
        "type": "command",
        "bash": "bash .github/hooks/scripts/print-pipeline-summary.sh"
      }
    ]
  }
}
```

The repository-level hook configuration is stored under:

```text
.github/hooks/
```

The configuration uses:

```text
version: 1
```

and defines the required lifecycle events inside the `hooks` object.

---

# Hook Script Files to Create

Store all scripts under:

```text
.github/hooks/scripts/
```

| Script                                            | Hook Type       | Purpose                |
| ------------------------------------------------- | --------------- | ---------------------- |
| `.github/hooks/scripts/log-agent-invocation.sh`   | `subagentStart` | Log subagent startup   |
| `.github/hooks/scripts/validate-output-file.sh`   | `postToolUse`   | Validate output files  |
| `.github/hooks/scripts/print-pipeline-summary.sh` | `sessionEnd`    | Print pipeline summary |

All scripts must:

* Start with `#!/bin/bash`
* Be executable
* Be informational or validation-oriented
* Never intentionally block the pipeline
* Never replace orchestrator gating logic

---

# Deliverables Checklist

* `.github/hooks/scripts/log-agent-invocation.sh` created
* `.github/hooks/scripts/validate-output-file.sh` created
* `.github/hooks/scripts/print-pipeline-summary.sh` created
* `.github/hooks/pipeline-hooks.json` created
* All three hooks configured
* Scripts made executable
* All files committed

---

# Verification

## 1. Validate Hook Configuration

Run:

```bash
python -m json.tool .github/hooks/pipeline-hooks.json
```

Confirm that the JSON is valid.

---

## 2. Verify Agent Invocation Logging

Run the orchestrator:

```text
@orchestrator process user-stories/user-story-1.md
```

Confirm that the `subagentStart` hook adds an entry similar to:

```text
### 2026-10-06T12:00:00Z — Subagent started
```

to:

```text
docs/changelog.md
```

---

## 3. Verify Output Validation

Ask the pipeline to produce a test document:

```text
docs/test-hook.md
```

Confirm that the `postToolUse` hook executes and reports the output validation result.

Delete the test file after verification.

---

## 4. Verify Pipeline Summary

End the Copilot session after running the pipeline.

Confirm that the summary contains:

```text
PIPELINE RUN SUMMARY
```

and reports:

* Requirements status
* Architecture status
* Design review status
* Implementation plan status
* Documentation sync status
* Code review status
* Verification status
* Source file count
* Test file count

---

## 5. Verify Scripts

Run:

```bash
bash .github/hooks/scripts/log-agent-invocation.sh
bash .github/hooks/scripts/validate-output-file.sh
bash .github/hooks/scripts/print-pipeline-summary.sh
```

Confirm that all scripts execute without errors.

---

# Final Hook Flow

```text
                ┌──────────────────────┐
                │     Orchestrator     │
                └──────────┬───────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Subagent Start │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Log Invocation  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     Subagent    │
                  │     Executes    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Post Tool Use  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Validate Output │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Pipeline Continues
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Session End   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Pipeline Summary│
                  └─────────────────┘
```

## Phase 5 Success Criteria

Phase 5 is complete when:

1. GitHub Copilot hooks are configured under `.github/hooks/`.
2. `subagentStart` logs pipeline agent activity.
3. `postToolUse` validates relevant output files.
4. `sessionEnd` prints the pipeline summary.
5. Hooks do not replace or bypass orchestrator gates.
6. The complete pipeline can run without manually invoking individual specialist agents.
7. All hook configuration and scripts are committed to the repository.
