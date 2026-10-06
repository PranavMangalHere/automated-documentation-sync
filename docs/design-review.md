# Design Review: Task List CLI

## Summary

Reviewed `docs/architecture.md` against `docs/requirements.md`, including functional and non-functional requirements, component boundaries, persistence, failure behavior, and security. The design is appropriately small for a local, standard-library CLI, and its storage-error handling is generally aligned with the requirements. Two contract details need resolution before implementation: CLI parser failures must reliably use exit code 1, and the persisted-state validation must reconcile sequential IDs with the allowed ID-counter invariant.

**Overall recommendation: Request Changes**

## Risk Table

| Risk | Severity (Critical/Major/Minor) | Recommendation |
| --- | --- | --- |
| CLI parser exit codes are underspecified. The architecture allows `argparse` only "where compatible" but does not define how parser-generated errors (such as an unknown command or missing argument) become exit code 1. Default parser behavior can return exit code 2, conflicting with FR-8/AC-11. References: `docs/architecture.md`, “Components and Interfaces” and “Public CLI Contracts”; `docs/requirements.md`, FR-8 and AC-11. | Major | Specify and implement one CLI error-mapping rule for all invalid commands and input: write a clear message to stderr and exit 1. Preserve exit 0 for top-level help. Add acceptance coverage for unknown commands and malformed/missing command arguments. |
| Persisted-state validation does not guarantee sequential IDs. It requires unique positive IDs and `next_id` greater than the maximum, which permits a state such as IDs 1 and 3 with `next_id` 4. With no delete operation in scope, that state conflicts with FR-3/AC-4's sequential allocation contract. References: `docs/architecture.md`, “Persistence Contract” and “Requirements Traceability”; `docs/requirements.md`, FR-3 and AC-4. | Minor | Define the version-1 invariant explicitly. Given the stated scope, reject gaps and require allocated IDs to be exactly `1` through `next_id - 1`, or document and justify another representation that still proves sequential, non-reused allocation. Include a malformed-state test. |

## Design Decisions Confirmed

- A local JSON file in the current working directory and standard-library-only implementation satisfy the requirements without introducing unnecessary services or dependencies (`docs/architecture.md`, “Persistence Contract” and “Technology Choices and Dependencies”; `docs/requirements.md`, FR-6 and AC-13).
- A version field, strict validation, and refusal to treat read or parse failures as an empty list support the data-preservation requirements (`docs/architecture.md`, “Data Flow” and “Persistence Contract”; `docs/requirements.md`, FR-7 and AC-10).
- Same-directory temporary-file replacement is a proportionate safeguard against truncating the existing document during an incomplete write (`docs/architecture.md`, “Data Flow”). The stated exclusion of concurrent writers is consistent with requirements scope (`docs/requirements.md`, “Assumptions and Out of Scope”).
- Separating CLI formatting, task behavior, and persistence into three components is appropriate for the small application and provides clear locations for focused tests (`docs/architecture.md`, “Components and Interfaces”).
- Readable plain-text output, stderr errors, help support, and the absence of networking address the accessibility and security requirements at the requested scope (`docs/architecture.md`, “Public CLI Contracts” and “Security Considerations”).

## Required Changes Before Implementation

1. Resolve CLI parser error handling so every invalid command or command input exits 1 with a clear stderr message, while `-h` and `--help` exit 0. Cover these outcomes in the CLI contract and tests. (Architecture: “Components and Interfaces,” “Public CLI Contracts”; requirements: FR-8, FR-9, AC-1, AC-11.)
2. Define the exact valid version-1 ID sequence invariant and align repository validation with FR-3/AC-4. Under the current no-deletion scope, either require contiguous allocated IDs through `next_id - 1` or provide another explicit mechanism that proves sequential allocation and non-reuse. (Architecture: “Persistence Contract”; requirements: FR-3, AC-4.)
