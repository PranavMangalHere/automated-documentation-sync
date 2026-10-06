# Task List CLI Architecture

## Changelog

- 2026-10-06: Clarified the version-1 contiguous ID invariant to match repository validation.

**Source:** `docs/requirements.md`  
**Author:** Architecture Agent  
**Date:** 2026-10-06

**Approved design decisions:** Storage uses a versioned JSON document with a persisted `next_id` counter. With task deletion out of scope, stored IDs must be contiguous from 1 through `next_id - 1`, so IDs are never reused. The `add` command accepts multiple unquoted words, joins them with spaces, and rejects a description that is empty or contains only whitespace.

**Assumptions:**
- The application is packaged so `python -m task_list` resolves the CLI entry point; installation and repository packaging details are implementation concerns.
- A missing `.task-list.json` represents an empty list and initializes the next ID to 1.
- Concurrent writers are out of scope, as specified in the requirements.
- The storage schema begins at version 1. Unsupported versions are reported as storage errors rather than rewritten.

## Executive Summary

The Task List CLI is a local, single-user Python command-line application for adding, listing, and completing tasks. A thin command interface delegates task operations to a task service, which uses a JSON repository in the process's current working directory. The design uses only Python's standard library and does not require a network connection or external service.

The repository validates the versioned document before allowing mutations. It stores the next ID independently of the current task collection, preserving monotonic ID allocation even when the list has no task with the highest previously allocated ID. Read, parse, schema, and write failures are surfaced on stderr with exit code 1; failed reads never become an empty list and are never followed by a replacement write.

## Component Diagram

```text
User / shell
    |
    v
`python -m task_list`
    |
    v
CLI parser and dispatcher -----> stderr / exit status
    |
    v
Task service
    |
    v
JSON task repository <--------> .task-list.json
    |
    v
stdout
```

## Components and Interfaces

| Component | Responsibility | Public interface | Data exchanged |
| --- | --- | --- | --- |
| CLI parser and dispatcher | Expose `add`, `list`, and `complete`; parse arguments; route requests; format user-facing output and errors. | `python -m task_list`; top-level `-h` and `--help`; command forms below. | Command arguments, task results, plain-text output, stderr errors, process exit status. |
| Task service | Enforce task behavior, status transitions, description validation, creation order, and ID allocation. | `add(description)`, `list_tasks()`, `complete(task_id)`. | Task descriptions, positive integer IDs, task records, domain errors. |
| JSON task repository | Load, validate, and persist the versioned data document at `.task-list.json` in the current working directory. | Internal `load()` and `save(state)` operations used by the service. | Versioned JSON state; storage errors for missing permissions, malformed content, unsupported schema, or failed writes. |

The CLI maps expected command and storage failures to a clear stderr message and exit code 1. Successful commands write results to stdout and exit 0. Help exits 0 and describes all three commands. Invalid commands and invalid command input follow the required exit code 1 contract rather than being exposed as uncaught exceptions.

## Data Flow

1. The user invokes `python -m task_list` in a working directory. The CLI parses the command and passes the operation to the task service.
2. The service asks the repository to load `.task-list.json`. If the file does not exist, the repository supplies a valid empty state with `next_id` set to 1. If it exists but cannot be read, parsed, or validated, processing stops with an error; no mutation or replacement is attempted.
3. For `add`, the CLI accepts one or more positional words and joins them with single spaces. The service rejects an empty or whitespace-only resulting description, creates a pending task using `next_id`, increments `next_id`, persists the updated state, and returns the allocated ID for stdout.
4. For `list`, the service returns tasks in creation order. The CLI prints one line per task with ID, status, and description, or prints `No tasks found` for an empty collection.
5. For `complete`, the service finds the requested ID, rejects an unknown or already-complete task, changes a pending task's status to complete, persists the state, and returns a confirmation for stdout.

For mutations, the repository validates the loaded state before saving. Saving should use a temporary file in the same directory followed by replacement of the storage file, so an incomplete write does not truncate the existing document. A failure before replacement leaves the prior document intact and is reported to the caller. The design does not promise coordination between concurrent writers.

## Public CLI Contracts

No network endpoints are exposed. The user-facing interface is the module command:

| Command | Input | Success output and status | Failure behavior |
| --- | --- | --- | --- |
| `python -m task_list add <word> [<word> ...]` | One or more unquoted words; words are joined with spaces. | Prints the new positive integer ID; exit 0. | Empty/whitespace-only description or storage failure: clear stderr error; exit 1. |
| `python -m task_list list` | None. | One readable `ID status description` line per task in creation order; `No tasks found` when empty; exit 0. | Storage failure: clear stderr error; exit 1. |
| `python -m task_list complete <id>` | Positive integer task ID. | Marks a pending task complete and prints confirmation; exit 0. | Invalid/unknown ID, already-complete task, or storage failure: clear stderr error; exit 1. |
| `python -m task_list -h` or `--help` | None. | Help describing `add`, `list`, and `complete`; exit 0. | Not applicable. |

Invalid commands produce a clear stderr error and exit 1. Exact punctuation for task lines and confirmations is intentionally unspecified by the requirements; formatting must include the required information and remain readable plain text.

## Persistence Contract

The file `.task-list.json` resides in the current working directory. The version 1 document has this shape:

```json
{
  "version": 1,
  "next_id": 3,
  "tasks": [
    {"id": 1, "status": "pending", "description": "Buy groceries"},
    {"id": 2, "status": "complete", "description": "Call the dentist"}
  ]
}
```

`version` identifies the storage format, `next_id` is the next positive integer to allocate, and `tasks` is ordered by creation. Each task has a positive integer `id`, a `pending` or `complete` status, and a non-whitespace description. The repository validates required fields, types, statuses, and the contiguous sequence invariant: task IDs in creation order must be exactly `1` through `next_id - 1`, so an empty task list requires `next_id` to be 1. Unknown or malformed content is reported rather than silently discarded. Because deletion is out of scope, persisting `next_id` alongside this validated sequence preserves allocation order and prevents ID reuse.

## Technology Choices and Dependencies

- Python standard library only, as required. The CLI may use `argparse` where compatible with the required exit-code contract, plus standard filesystem and JSON facilities.
- JSON is chosen for the local human-readable persistence format. The explicit version field allows future format evolution to be detected instead of misread.
- The current working directory is the only storage location and integration boundary. There are no external APIs, services, credentials, or third-party package dependencies.

## Deployment and Runtime Considerations

The application runs as a short-lived local process via `python -m task_list`; Python must be available in the invoking environment. The command reads and writes only `.task-list.json` in its current working directory. The requirements specify no exact minimum Python version, installation mechanism, latency target, or maximum task count; those remain packaging/runtime decisions for implementation.

This is a single-user local tool, not a highly available service. There is no server, background worker, network dependency, or multi-process locking. Concurrent modifications are out of scope. Storage operations should preserve the existing file on failed writes where possible, and malformed or unreadable data must never trigger initialization or overwrite behavior.

## Security Considerations

- No authentication, network access, secrets, or external service credentials are needed.
- Task content is treated as plain text and emitted as plain text; it is not evaluated as code or interpreted as markup.
- The repository accepts only the expected JSON structure and task statuses, and it reports invalid data without replacing it.
- The file inherits access controls of the current directory and operating system. Users are responsible for protecting local task data with filesystem permissions and backups.
- Error messages should be actionable without exposing unrelated file contents. The application does not claim encryption or protection against another process with access to the same account.

## Operations: Logging, Monitoring, and Backups

The CLI reports command and storage errors on stderr and uses process exit status for scripting. It has no long-running process, telemetry, monitoring service, or separate logging subsystem; successful command results go to stdout. Backups are not automated, so users should back up `.task-list.json` using their normal local-file practices. No retry is performed after parsing, permission, or persistence errors, because retrying or initializing could obscure data loss or access problems.

## Requirements Traceability

| Requirement | Architectural support |
| --- | --- |
| FR-1 | Module entry point and CLI dispatcher expose `add`, `list`, and `complete`. |
| FR-2 | `add` validates a non-whitespace description, creates a pending task, persists it, and prints its ID; invalid input maps to stderr and exit 1. |
| FR-3 | Persisted `next_id` starts at 1 and advances on each successful add; stored IDs are exactly `1` through `next_id - 1` in creation order. |
| FR-4 | Listing returns creation-ordered records and formats ID, status, and description, including the required empty-list output. |
| FR-5 | The task service permits pending-to-complete once and rejects unknown or already-complete IDs. |
| FR-6 | The repository reads and writes `.task-list.json` relative to the current working directory; a missing file means empty state. |
| FR-7 | Repository read, parse, validation, and write failures are reported; invalid reads do not become empty state or lead to overwrite. |
| FR-8 | CLI dispatch reports invalid commands on stderr with exit 1. |
| FR-9 | Help is provided by the CLI and the design uses only Python standard-library facilities. |
| NFR: Performance | Local JSON read/write; no numeric latency or capacity target is introduced. |
| NFR: Security | No external service; filesystem permissions protect local data; content is plain text and malformed storage is not silently replaced. |
| NFR: Reliability | Persistent state, validated storage, persisted ID counter, and explicit failure reporting. |
| NFR: Accessibility | Readable plain-text output, stderr errors, and conventional top-level help flags. |
| AC-1 through AC-13 | The CLI contracts, persistence format, state transitions, storage behavior, and stdlib-only technology choice collectively address the acceptance criteria. |

## Open Questions and Trade-offs

- **JSON versus a database:** JSON is simple, inspectable, and satisfies the local-file and standard-library constraints; it is less suitable for large datasets or concurrent writers, both outside the current scope.
- **Version migration:** Version 1 is defined, but no migration behavior is needed yet. Unsupported versions should fail clearly until a migration requirement exists.
- **Atomic replacement:** A same-directory temporary file and replacement reduce the chance of a partial document, but filesystem and process-crash guarantees vary. This is not a transaction system and does not provide concurrent-writer safety.
- **Packaging and Python support range:** The module invocation is required, but package layout, install method, and minimum supported Python version are not specified and should be settled during implementation planning.
- **Exact output wording:** Required fields and error channels/status are fixed; task-line punctuation and success-message wording remain implementation choices.