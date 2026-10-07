"""Business rules for task creation, listing, and completion."""

from dataclasses import replace
from typing import Iterable

from task_list.models import Task, TaskState


class TaskError(Exception):
    """Base exception for expected task-operation failures."""


class InvalidDescriptionError(TaskError):
    """Raised when a task description is empty or whitespace-only."""


class InvalidTaskIdError(TaskError):
    """Raised when a task ID is not a positive integer."""


class TaskNotFoundError(TaskError):
    """Raised when the requested task does not exist."""


class TaskAlreadyCompleteError(TaskError):
    """Raised when completing a task that is already complete."""


class TaskService:
    """Apply task rules to an in-memory state."""

    def __init__(self, tasks: Iterable[Task] = (), next_id: int = 1) -> None:
        self._tasks = list(tasks)
        self._next_id = next_id

    def add(self, description: str) -> Task:
        """Create a pending task and allocate its sequential ID."""
        if not description.strip():
            raise InvalidDescriptionError("Task description cannot be empty.")
        task = Task(self._next_id, "pending", description)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def list_tasks(self) -> tuple[Task, ...]:
        """Return tasks in creation order."""
        return tuple(self._tasks)

    def complete(self, task_id: int) -> Task:
        """Mark a pending task complete and return the updated task."""
        if type(task_id) is not int or task_id < 1:
            raise InvalidTaskIdError("Task ID must be a positive integer.")
        for index, task in enumerate(self._tasks):
            if task.id == task_id:
                if task.status == "complete":
                    raise TaskAlreadyCompleteError(
                        f"Task {task_id} is already complete."
                    )
                completed = replace(task, status="complete")
                self._tasks[index] = completed
                return completed
        raise TaskNotFoundError(f"Task {task_id} was not found.")

    def state(self) -> TaskState:
        """Return an immutable snapshot suitable for persistence."""
        return TaskState(tuple(self._tasks), self._next_id)