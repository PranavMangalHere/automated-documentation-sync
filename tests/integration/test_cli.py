"""Subprocess tests for real module invocation and persistent workflows."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


SOURCE_DIR = Path(__file__).resolve().parents[2] / "src"


def run_cli(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Invoke the CLI with source imports available from an isolated directory."""
    environment = os.environ.copy()
    existing_path = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(SOURCE_DIR), existing_path) if part
    )
    return subprocess.run(
        [sys.executable, "-m", "task_list", *arguments],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_add_list_complete_persists_across_processes(tmp_path: Path) -> None:
    first = run_cli(tmp_path, "add", "Buy", "groceries")
    second = run_cli(tmp_path, "add", "Call dentist")
    listed = run_cli(tmp_path, "list")
    completed = run_cli(tmp_path, "complete", "1")
    listed_after = run_cli(tmp_path, "list")

    assert first.returncode == second.returncode == 0
    assert first.stdout.strip() == "1"
    assert second.stdout.strip() == "2"
    assert listed.stdout.splitlines() == [
        "1 pending Buy groceries",
        "2 pending Call dentist",
    ]
    assert completed.returncode == 0
    assert "completed" in completed.stdout
    assert listed_after.stdout.splitlines()[0] == "1 complete Buy groceries"


def test_missing_storage_lists_empty_and_help_succeeds(tmp_path: Path) -> None:
    empty = run_cli(tmp_path, "list")
    short_help = run_cli(tmp_path, "-h")
    long_help = run_cli(tmp_path, "--help")
    assert empty.returncode == 0
    assert empty.stdout.strip() == "No tasks found"
    for result in (short_help, long_help):
        assert result.returncode == 0
        assert all(command in result.stdout for command in ("add", "list", "complete"))
        assert result.stderr == ""


@pytest.mark.parametrize(
    "arguments",
    [(), ("unknown",), ("add",), ("add", "   "), ("complete",),
     ("complete", "bad"), ("complete", "0"), ("complete", "1", "extra")],
)
def test_invalid_invocation_exits_one_on_stderr(
    tmp_path: Path, arguments: tuple[str, ...]
) -> None:
    result = run_cli(tmp_path, *arguments)
    assert result.returncode == 1
    assert result.stderr.strip()
    assert result.stdout == ""


def test_unknown_and_already_complete_task_ids_are_errors(tmp_path: Path) -> None:
    unknown = run_cli(tmp_path, "complete", "1")
    run_cli(tmp_path, "add", "Task")
    assert run_cli(tmp_path, "complete", "1").returncode == 0
    already_complete = run_cli(tmp_path, "complete", "1")
    assert unknown.returncode == already_complete.returncode == 1
    assert unknown.stderr.strip() and already_complete.stderr.strip()


@pytest.mark.parametrize(
    "stored",
    [
        '{"version": 1, "next_id": 1, "tasks": [',
        '{"version": 1, "next_id": 4, "tasks": '
        '[{"id": 1, "status": "pending", "description": "one"}, '
        '{"id": 3, "status": "pending", "description": "three"}]}',
    ],
)
def test_bad_storage_exits_one_without_overwriting(
    tmp_path: Path, stored: str
) -> None:
    path = tmp_path / ".task-list.json"
    path.write_text(stored, encoding="utf-8")
    result = run_cli(tmp_path, "add", "Do not overwrite")
    assert result.returncode == 1
    assert result.stderr.strip()
    assert result.stdout == ""
    assert path.read_text(encoding="utf-8") == stored


def test_storage_read_failure_is_reported(tmp_path: Path) -> None:
    (tmp_path / ".task-list.json").mkdir()
    result = run_cli(tmp_path, "list")
    assert result.returncode == 1
    assert result.stderr.strip()
    assert result.stdout == ""