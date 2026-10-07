"""Tests for CLI help, argument errors, and dispatch behavior."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Sequence

import pytest

from task_list.cli import main


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_top_level_help_exits_successfully(flag: str) -> None:
    output = StringIO()
    errors = StringIO()
    with redirect_stdout(output), redirect_stderr(errors):
        status = main([flag])
    assert status == 0
    assert all(command in output.getvalue() for command in ("add", "list", "complete"))
    assert errors.getvalue() == ""


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["unknown"],
        ["add"],
        ["add", "   "],
        ["add", "valid", "--unexpected"],
        ["complete"],
        ["complete", "abc"],
        ["complete", "0"],
        ["complete", "-1"],
        ["complete", "1", "extra"],
    ],
)
def test_invalid_command_or_input_exits_one(arguments: Sequence[str]) -> None:
    output = StringIO()
    errors = StringIO()
    with redirect_stdout(output), redirect_stderr(errors):
        status = main(arguments)
    assert status == 1
    assert errors.getvalue().strip().startswith("error:")
    assert output.getvalue() == ""