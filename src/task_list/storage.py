"""Strict version-1 JSON persistence for task state."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from task_list.models import Task, TaskState


class StorageError(Exception):
    """Raised when task state cannot safely be read or persisted."""


class JsonTaskRepository:
    """Load and atomically save state in a working-directory JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path if path is not None else Path.cwd() / ".task-list.json"

    def load(self) -> TaskState:
        """Read and validate the version-1 task document."""
        try:
            raw = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return TaskState((), 1)
        except (OSError, UnicodeError) as error:
            raise StorageError(f"Cannot read {self.path.name}: {error}") from error
        try:
            document = json.loads(raw)
            return self._decode(document)
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise StorageError(f"Invalid {self.path.name}: {error}") from error

    def save(self, state: TaskState) -> None:
        """Validate and atomically replace the stored version-1 document."""
        try:
            self._validate_state(state)
        except ValueError as error:
            raise StorageError(f"Invalid task state: {error}") from error
        document = {
            "version": 1,
            "next_id": state.next_id,
            "tasks": [
                {"id": task.id, "status": task.status,
                 "description": task.description}
                for task in state.tasks
            ],
        }
        temporary_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=f".{self.path.name}.", suffix=".tmp", delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name
                json.dump(document, temporary_file, ensure_ascii=False, indent=2)
                temporary_file.write("\n")
            os.replace(temporary_path, self.path)
        except (OSError, TypeError, ValueError) as error:
            raise StorageError(f"Cannot save {self.path.name}: {error}") from error
        finally:
            if temporary_path is not None and os.path.exists(temporary_path):
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass

    @classmethod
    def _decode(cls, document: Any) -> TaskState:
        if not isinstance(document, dict) or set(document) != {
            "version", "next_id", "tasks"
        }:
            raise ValueError("expected version, next_id, and tasks fields")
        if type(document["version"]) is not int or document["version"] != 1:
            raise ValueError("unsupported storage version")
        raw_tasks = document["tasks"]
        if not isinstance(raw_tasks, list):
            raise ValueError("tasks must be a list")
        tasks = tuple(cls._decode_task(raw_task) for raw_task in raw_tasks)
        state = TaskState(tasks, document["next_id"])
        cls._validate_state(state)
        return state

    @staticmethod
    def _decode_task(raw_task: Any) -> Task:
        if not isinstance(raw_task, dict) or set(raw_task) != {
            "id", "status", "description"
        }:
            raise ValueError("each task must have id, status, and description")
        task_id = raw_task["id"]
        status = raw_task["status"]
        description = raw_task["description"]
        if type(task_id) is not int or task_id < 1:
            raise ValueError("task IDs must be positive integers")
        if status not in ("pending", "complete"):
            raise ValueError("task status must be pending or complete")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("task descriptions must be non-empty strings")
        return Task(task_id, status, description)

    @staticmethod
    def _validate_state(state: TaskState) -> None:
        if type(state.next_id) is not int or state.next_id < 1:
            raise ValueError("next_id must be a positive integer")
        if not isinstance(state.tasks, tuple):
            raise ValueError("tasks must be a tuple")
        if state.next_id != len(state.tasks) + 1:
            raise ValueError("task IDs must be creation-ordered from 1 to next_id - 1")
        for expected_id, task in enumerate(state.tasks, start=1):
            if not isinstance(task, Task):
                raise ValueError("tasks must contain task records")
            if type(task.id) is not int or task.id != expected_id:
                raise ValueError("task IDs must be creation-ordered from 1 to next_id - 1")
            if task.status not in ("pending", "complete"):
                raise ValueError("task has an invalid ID or status")
            if not isinstance(task.description, str) or not task.description.strip():
                raise ValueError("task description must be a non-empty string")