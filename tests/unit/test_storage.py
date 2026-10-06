"""Tests for version-1 JSON validation and durable storage behavior."""

import json
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from task_list.models import Task, TaskState
from task_list.storage import JsonTaskRepository, StorageError


def document(task_ids: list[int], next_id: int) -> dict[str, object]:
    """Build a valid-shaped storage document for invariant test cases."""
    return {
        "version": 1,
        "next_id": next_id,
        "tasks": [
            {"id": task_id, "status": "pending", "description": f"Task {task_id}"}
            for task_id in task_ids
        ],
    }


def test_missing_file_is_empty_state_and_round_trips(tmp_path: Path) -> None:
    repository = JsonTaskRepository(tmp_path / ".task-list.json")
    assert repository.load() == TaskState((), 1)
    repository.save(TaskState((Task(1, "pending", "Task one"),), 2))
    assert repository.load() == TaskState((Task(1, "pending", "Task one"),), 2)


@pytest.mark.parametrize(
    "stored",
    [
        document([1, 3], 4),
        document([2], 3),
        document([2, 1], 3),
        document([1], 3),
        document([], 2),
        {"version": 2, "next_id": 1, "tasks": []},
        {"version": 1, "next_id": 1, "tasks": "not a list"},
        {"version": 1, "next_id": 1, "tasks": [], "extra": True},
    ],
)
def test_invalid_documents_are_rejected_without_modification(
    tmp_path: Path, stored: dict[str, object]
) -> None:
    path = tmp_path / ".task-list.json"
    original = json.dumps(stored)
    path.write_text(original, encoding="utf-8")
    with pytest.raises(StorageError):
        JsonTaskRepository(path).load()
    assert path.read_text(encoding="utf-8") == original


def test_malformed_json_is_not_treated_as_empty(tmp_path: Path) -> None:
    path = tmp_path / ".task-list.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(StorageError, match="Invalid"):
        JsonTaskRepository(path).load()


def test_invalid_utf8_is_reported_as_storage_error(tmp_path: Path) -> None:
    path = tmp_path / ".task-list.json"
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(StorageError, match="Cannot read"):
        JsonTaskRepository(path).load()


def test_read_error_is_reported(tmp_path: Path) -> None:
    path = tmp_path / ".task-list.json"
    path.mkdir()
    with pytest.raises(StorageError, match="Cannot read"):
        JsonTaskRepository(path).load()


def test_failed_replace_preserves_existing_file(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    path = tmp_path / ".task-list.json"
    path.write_text("previous contents", encoding="utf-8")

    def fail_replace(source: str, destination: Path) -> None:
        raise OSError("injected replacement failure")

    monkeypatch.setattr("task_list.storage.os.replace", fail_replace)
    with pytest.raises(StorageError, match="Cannot save"):
        JsonTaskRepository(path).save(TaskState((), 1))
    assert path.read_text(encoding="utf-8") == "previous contents"


def test_save_rejects_non_contiguous_state(tmp_path: Path) -> None:
    repository = JsonTaskRepository(tmp_path / ".task-list.json")
    invalid = TaskState((Task(2, "pending", "Task two"),), 3)
    with pytest.raises(StorageError, match="creation-ordered"):
        repository.save(invalid)
    assert not repository.path.exists()