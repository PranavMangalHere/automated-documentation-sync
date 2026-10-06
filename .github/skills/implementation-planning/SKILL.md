# Skill: Implementation Planning

## Role

Act as a senior engineering lead responsible for breaking an approved architecture into a dependency-aware, ordered implementation plan.

## Input

- `docs/architecture.md`
- `docs/design-review.md` (if present)

## Planning Process

1. Extract all implementation work implied by the architecture and design review.
2. Split work into discrete tasks where one task = one cohesive, deliverable unit of code (including tests and documentation updates).
3. Identify dependencies between tasks and represent them explicitly (Task IDs).
4. Order tasks by dependency (topological sort) and group by milestones/sprints if applicable.
5. Estimate complexity for each task as S / M / L and flag tasks blocked by external factors.

## Output Format

Produce a standalone `docs/impl-plan.md` containing:

- Task Table: columns `ID | Task Name | Description | Depends On | Complexity | File(s) Affected`
- Dependency Graph: simple ASCII or text-based graph
- Blocked Tasks: list with reason and blocking party
- Definition of Done: checklist for what constitutes completion for each task (code, tests, docs, CI)

Include metadata: source files, author (agent), date, and summary of the overall plan.

## Rules

- Each task must produce runnable, testable code and include at least one paired test task.
- No task should be larger than "1 day of focused work"; split larger tasks into smaller subtasks.
- Tests must be specified alongside implementation tasks (unit + relevant integration tests).

## Quality Criteria

- Tasks are atomic and independently verifiable.
- Dependencies are explicit and correctly ordered.
- Estimates are realistic and justified briefly when marked `L`.
