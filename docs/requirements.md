# Requirements: Task List CLI

## Summary

People managing daily tasks need a simple local command-line tool to add, list, and complete tasks without relying on an external service. The tool is invoked with `python -m task_list`, persists tasks in `.task-list.json` in the current working directory, and uses only the Python standard library.

## Stakeholders and User Roles

- **Task list user:** adds tasks, reviews their status, and marks pending tasks complete.
- **Project maintainer:** needs predictable CLI behavior and testable error handling.

## Functional Requirements

- **FR-1:** The application shall be invokable as `python -m task_list` and provide `add`, `list`, and `complete` commands.
- **FR-2:** `add` shall accept a non-empty description, store a new task with `pending` status, and print its ID. An empty description shall produce a clear stderr error and exit code 1.
- **FR-3:** Task IDs shall be sequential positive integers starting at 1. IDs shall remain stable and shall never be reused.
- **FR-4:** `list` shall print tasks in creation order, one readable line per task containing its ID, status (`pending` or `complete`), and description. An empty list shall print `No tasks found` and exit code 0.
- **FR-5:** `complete` shall accept a task ID, mark a matching pending task complete, and print a confirmation. An unknown ID or an already-complete task shall produce a clear stderr error and exit code 1.
- **FR-6:** Tasks shall persist between invocations in `.task-list.json` in the current working directory. A missing storage file shall be treated as an empty task list.
- **FR-7:** Malformed, unreadable, or unwritable `.task-list.json` shall produce a clear stderr error and exit code 1. The application shall not silently replace or overwrite task data when storage access or parsing fails.
- **FR-8:** An invalid command shall produce a clear stderr error and exit code 1.
- **FR-9:** Top-level `-h` and `--help` shall be supported, exit with code 0, and describe the available commands.

## Non-Functional Requirements

- **Performance:** Commands operate on a local JSON file. No quantitative latency or maximum task-count target is specified.
- **Security:** The application shall use no external service and shall use only the Python standard library. It shall not silently discard or replace task data after a storage read/parse failure.
- **Reliability:** Task data shall persist across commands, IDs shall not be reused, and storage failures shall be reported rather than treated as an empty list.
- **Accessibility:** Output shall be readable plain text; errors shall be written to stderr, and command help shall be available using conventional `-h` and `--help` flags.

## Acceptance Criteria

- **AC-1 (FR-1, FR-9):** Running `python -m task_list -h` or `python -m task_list --help` exits 0 and describes `add`, `list`, and `complete`.
- **AC-2 (FR-2, FR-3, FR-6):** Adding a non-empty description creates a pending task in `.task-list.json`, prints its positive integer ID, and makes the task available to a later invocation.
- **AC-3 (FR-2):** Adding an empty description prints a clear error to stderr and exits 1.
- **AC-4 (FR-3):** The first created task has ID 1; each subsequently created task receives the next positive integer in creation order, and previously allocated IDs are never reused.
- **AC-5 (FR-4):** Listing tasks prints one readable line per task in creation order, with ID, status, and description on each line.
- **AC-6 (FR-4, FR-6):** When there are no tasks, including when the storage file is missing, `list` prints `No tasks found` and exits 0.
- **AC-7 (FR-5):** Completing an existing pending task changes its status to complete, persists that status, and prints a confirmation.
- **AC-8 (FR-5):** Completing an unknown task ID prints a clear error to stderr and exits 1.
- **AC-9 (FR-5):** Completing a task that is already complete prints a clear error to stderr and exits 1.
- **AC-10 (FR-7):** For malformed, unreadable, or unwritable `.task-list.json`, the relevant command prints a clear error to stderr and exits 1; existing task data is not silently overwritten.
- **AC-11 (FR-8):** An invalid command prints a clear error to stderr and exits 1.
- **AC-12 (FR-2, FR-4, FR-5, FR-6):** A task added in one invocation remains available to later `list` and `complete` invocations using the same working directory.
- **AC-13 (FR-1):** The implementation uses only Python standard-library modules.

## Assumptions and Out of Scope

- Task descriptions are considered non-empty when they contain at least one non-whitespace character.
- The storage file is local to the current working directory; sharing or synchronizing task lists across directories or users is not required.
- Editing, deleting, searching, sorting, due dates, priorities, concurrent writers, and external integrations are out of scope.
- No specific task-line punctuation, JSON schema, performance target, or maximum task count is specified beyond the required fields and behavior above.

## Traceability

| Requirement ID | Acceptance Criteria | Test IDs |
| --- | --- | --- |
| FR-1 | AC-1, AC-13 | T-CLI-001, T-CLI-002 |
| FR-2 | AC-2, AC-3, AC-12, AC-13 | T-ADD-001, T-ADD-002, T-PERSIST-001 |
| FR-3 | AC-2, AC-4 | T-ID-001, T-ID-002 |
| FR-4 | AC-5, AC-6 | T-LIST-001, T-LIST-002 |
| FR-5 | AC-7, AC-8, AC-9 | T-COMPLETE-001, T-COMPLETE-002, T-COMPLETE-003 |
| FR-6 | AC-2, AC-6, AC-12 | T-PERSIST-001, T-PERSIST-002 |
| FR-7 | AC-10 | T-STORAGE-001, T-STORAGE-002, T-STORAGE-003 |
| FR-8 | AC-11 | T-CLI-003 |
| FR-9 | AC-1 | T-CLI-001, T-CLI-002 |

## Changelog

- Processed `user-stories/user-story-template.md`; created requirements for the Task List CLI.