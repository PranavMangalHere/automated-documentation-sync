"""Tests for task behavior independent of the CLI and filesystem."""

import pytest

from task_list.models import Task
from task_list.service import (
    InvalidDescriptionError,
    InvalidTaskIdError,
    TaskAlreadyCompleteError,
    TaskNotFoundError,
    TaskService,
)


def test_add_allocates_sequential_ids_and_lists_in_creation_order() -> None:
    service = TaskService()
    first = service.add("First task")
    second = service.add("Second task")
    assert (first.id, second.id) == (1, 2)
    assert service.list_tasks() == (first, second)
    assert first.status == second.status == "pending"


@pytest.mark.parametrize("description", ["", " ", "\t\n"])
def test_add_rejects_empty_descriptions(description: str) -> None:
    with pytest.raises(InvalidDescriptionError):
        TaskService().add(description)


def test_ids_continue_after_loading_existing_state() -> None:
    service = TaskService((Task(1, "complete", "Old task"),), next_id=2)
    assert service.add("New task").id == 2


def test_complete_changes_pending_task_only_once() -> None:
    service = TaskService()
    task = service.add("Task")
    assert service.complete(task.id).status == "complete"
    with pytest.raises(TaskAlreadyCompleteError):
        service.complete(task.id)


def test_complete_rejects_unknown_ids() -> None:
    with pytest.raises(TaskNotFoundError):
        TaskService().complete(1)


@pytest.mark.parametrize("task_id", [0, -1])
def test_complete_rejects_non_positive_ids(task_id: int) -> None:
    with pytest.raises(InvalidTaskIdError):
        TaskService().complete(task_id)


def test_complete_rejects_non_integer_ids() -> None:
    with pytest.raises(InvalidTaskIdError):
        TaskService().complete(True)