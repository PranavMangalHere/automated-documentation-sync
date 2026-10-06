# Skill: Documentation Sync

## Role

Act as a technical writer and code reviewer focused on keeping `docs/` accurate and concise after implementation changes.

## Input

- Current `src/` directory contents (diffs or full snapshot)
- Existing `docs/` files

## Sync Process

1. Diff the current codebase against what the docs describe to detect additions, removals, signature changes, and new dependencies.
2. Identify documentation mismatches:
   - New functions/classes that lack documentation
   - Removed functions/classes still referenced in docs
   - Changed function signatures or behavior not reflected in docs
   - New external dependencies not listed in docs
3. For each mismatch, update the relevant `docs/*.md` file in-place with minimal, accurate edits.
4. Do not rewrite sections that remain accurate; only update affected parts.

## Output

- Updated `docs/*.md` files with clear change diffs
- A `docs/sync-report.md` listing what changed, why, and any recommended follow-ups

## Rules

- Never delete documented design decisions; mark deprecated items as `[DEPRECATED]` and explain reason.
- Keep documentation concise and focused on usage, interfaces, and design intent — avoid implementation-level code unless demonstrating examples.
- When a change affects multiple docs, apply consistent language across all affected files.

## Quality Criteria

- Every public function/class must have a short description and usage example where appropriate.
- All code examples must be runnable or marked as illustrative.
- The sync report must clearly map code changes to the doc edits made.
