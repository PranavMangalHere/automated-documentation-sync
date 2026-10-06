"""Command-line interface for managing a local task list."""

import argparse
import sys
from typing import Sequence

from task_list.service import TaskError, TaskService
from task_list.storage import JsonTaskRepository, StorageError


class CLIUsageError(Exception):
    """Raised for invalid CLI syntax so all usage failures exit with status 1."""


class ContractArgumentParser(argparse.ArgumentParser):
    """Argument parser whose invalid-input contract uses exit code 1."""

    def error(self, message: str) -> None:
        raise CLIUsageError(message)


def _positive_id(value: str) -> int:
    try:
        task_id = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("task ID must be a positive integer") from error
    if task_id < 1:
        raise argparse.ArgumentTypeError("task ID must be a positive integer")
    return task_id


def _build_parser() -> ContractArgumentParser:
    parser = ContractArgumentParser(prog="python -m task_list")
    commands = parser.add_subparsers(dest="command", required=True)
    add_parser = commands.add_parser("add", help="add a task")
    add_parser.add_argument("description", nargs="+", help="task description")
    commands.add_parser("list", help="list tasks")
    complete_parser = commands.add_parser("complete", help="complete a task")
    complete_parser.add_argument("id", type=_positive_id, help="positive task ID")
    return parser


def _run_command(arguments: argparse.Namespace) -> None:
    repository = JsonTaskRepository()
    state = repository.load()
    service = TaskService(state.tasks, state.next_id)
    if arguments.command == "add":
        task = service.add(" ".join(arguments.description))
        repository.save(service.state())
        print(task.id)
    elif arguments.command == "list":
        tasks = service.list_tasks()
        if not tasks:
            print("No tasks found")
        for task in tasks:
            print(f"{task.id} {task.status} {task.description}")
    else:
        task = service.complete(arguments.id)
        repository.save(service.state())
        print(f"Task {task.id} completed.")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse a command, run it, and return the process exit status."""
    try:
        arguments = _build_parser().parse_args(argv)
        _run_command(arguments)
    except CLIUsageError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except (TaskError, StorageError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except SystemExit as exit_error:
        return int(exit_error.code or 0)
    return 0