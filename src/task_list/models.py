"""Data models for the Task List application."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    """A task and its current completion status."""

    id: int
    status: str
    description: str


@dataclass(frozen=True)
class TaskState:
    """Persisted tasks and the next ID to allocate."""

    tasks: tuple[Task, ...]
    next_id: int