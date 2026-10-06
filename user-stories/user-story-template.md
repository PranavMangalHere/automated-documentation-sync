# User Story: Task List CLI

**As a** person managing daily tasks,

**I want** a command-line tool that lets me add, list, and complete tasks,

**So that** I can keep a simple local task list without an external service.

## Details

- The tool is invoked from the command line as `python -m task_list`.
- The `add` command accepts a non-empty task description and prints the created task ID:
  `python -m task_list add "Buy groceries"`.
- The `list` command prints every task with its ID, status (`pending` or `complete`), and description:
  `python -m task_list list`.
- The `complete` command accepts a task ID, marks the matching pending task as complete, and prints a confirmation:
  `python -m task_list complete 1`.
- Tasks persist between commands in a JSON file in the current working directory named `.task-list.json`.
- A missing task storage file is treated as an empty task list.
- An empty description, an unknown task ID, or an invalid command prints a clear error to stderr and exits with code 1.
- Listing an empty task list prints `No tasks found` and exits with code 0.
- The tool uses only the Python standard library.

## Acceptance Criteria

1. Given a non-empty description, `add` stores a pending task and prints its ID.
2. Given one or more stored tasks, `list` prints each task's ID, status, and description.
3. Given an existing pending task ID, `complete` marks the task as complete and prints a confirmation.
4. Given an unknown task ID, `complete` prints a clear error to stderr and exits with code 1.
5. Given an empty task list, `list` prints `No tasks found` and exits with code 0.
6. Tasks added in one command are available to later `list` and `complete` commands.
7. The CLI help command exits with code 0 and describes the available commands.