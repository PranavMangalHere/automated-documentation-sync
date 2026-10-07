# Code Review

## Executive Summary and Scope

**Review result: Needs changes.** Reviewed every Python file under `src/` and `tests/` against `docs/requirements.md`, covering correctness, security, error handling, test coverage, dependency safety, performance, maintainability, and documentation alignment. Found one Major error-handling defect affecting FR-7 and one Minor CLI write-failure coverage gap. No source or test files were modified. Tests were not run, as requested.

## Findings

| File | Snippet | Finding | Severity | Recommendation |
| --- | --- | --- | --- | --- |
| [src/task_list/storage.py](../../src/task_list/storage.py#L31), [src/task_list/cli.py](../../src/task_list/cli.py#L71) | `json.loads(raw)`; handled exceptions exclude `RecursionError` | A sufficiently deeply nested JSON document can raise `RecursionError` during parsing. It is not converted to `StorageError`, and the CLI does not catch it, so malformed storage produces an uncaught traceback instead of the clear stderr error required by FR-7. | Major | Catch `RecursionError` at the storage parsing boundary and wrap it as `StorageError`, preserving the original file. Add a regression test using deeply nested JSON and assert a clean CLI error and exit code 1. |
| [tests/unit/test_storage.py](../../tests/unit/test_storage.py#L77), [src/task_list/cli.py](../../src/task_list/cli.py#L49) | Replacement failure is tested at repository level; CLI calls `repository.save(...)` | The repository test verifies that a failed atomic replace preserves existing contents, but no test exercises the CLI contract when saving fails: stderr error, exit code 1, and no success output. The unwritable-file portion of AC-10 is therefore not directly covered end to end. | Minor | Add a focused CLI test that injects a save/replace `OSError` and checks exit code, stderr, absence of stdout success, and preservation of existing data. |

## Requirement Cross-Reference

| Requirement | Implementation and test references | Review status |
| --- | --- | --- |
| FR-1 | [src/task_list/__main__.py](../../src/task_list/__main__.py#L3), [src/task_list/cli.py](../../src/task_list/cli.py#L29), [tests/integration/test_cli.py](../../tests/integration/test_cli.py#L31) | Implemented; invocation and workflows covered. |
| FR-2 | [src/task_list/service.py](../../src/task_list/service.py#L36), [src/task_list/cli.py](../../src/task_list/cli.py#L43), [tests/unit/test_service.py](../../tests/unit/test_service.py#L24) | Implemented; empty and non-empty descriptions covered. |
| FR-3 | [src/task_list/service.py](../../src/task_list/service.py#L40), [src/task_list/storage.py](../../src/task_list/storage.py#L104), [tests/unit/test_service.py](../../tests/unit/test_service.py#L15) | Sequential allocation and contiguous persisted IDs implemented. |
| FR-4 | [src/task_list/cli.py](../../src/task_list/cli.py#L52), [src/task_list/service.py](../../src/task_list/service.py#L45), [tests/integration/test_cli.py](../../tests/integration/test_cli.py#L31) | Implemented; list ordering and empty output covered. |
| FR-5 | [src/task_list/service.py](../../src/task_list/service.py#L49), [src/task_list/cli.py](../../src/task_list/cli.py#L57), [tests/integration/test_cli.py](../../tests/integration/test_cli.py#L76) | Implemented; completion, unknown ID, and already-complete cases covered. |
| FR-6 | [src/task_list/storage.py](../../src/task_list/storage.py#L22), [tests/unit/test_storage.py](../../tests/unit/test_storage.py#L25), [tests/integration/test_cli.py](../../tests/integration/test_cli.py#L31) | Implemented; missing-file behavior and persistence covered. |
| FR-7 | [src/task_list/storage.py](../../src/task_list/storage.py#L22), [src/task_list/storage.py](../../src/task_list/storage.py#L31), [src/task_list/cli.py](../../src/task_list/cli.py#L71), [tests/unit/test_storage.py](../../tests/unit/test_storage.py#L56), [tests/integration/test_cli.py](../../tests/integration/test_cli.py#L94) | **Violation:** deeply nested JSON can escape as an uncaught `RecursionError`. CLI write-failure behavior also lacks direct coverage. |
| FR-8 | [src/task_list/cli.py](../../src/task_list/cli.py#L17), [tests/unit/test_cli.py](../../tests/unit/test_cli.py#L38) | Invalid command and argument errors are reported with exit code 1. |
| FR-9 | [src/task_list/cli.py](../../src/task_list/cli.py#L25), [tests/unit/test_cli.py](../../tests/unit/test_cli.py#L13) | Top-level help is implemented and covered. |
| AC-13 | [src/task_list/cli.py](../../src/task_list/cli.py#L3), [src/task_list/storage.py](../../src/task_list/storage.py#L3), [pyproject.toml](../../pyproject.toml#L1) | Source uses standard-library modules; no runtime third-party dependency identified. |

## Overall Recommendation

**Request Changes.** Handle `RecursionError` from malformed storage before proceeding; add a regression test for that case. The CLI write-failure test is a lower-priority coverage improvement.