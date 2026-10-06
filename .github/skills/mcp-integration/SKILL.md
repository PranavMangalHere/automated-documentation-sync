# MCP Integration Skill

Purpose

This skill documents the Model Context Protocol (MCP) contract used by the pipeline to request and receive GitHub actions (specifically PR creation). It standardizes payloads, responses, error handling, and dry-run behavior so agents and the orchestrator interoperate reliably.

Contract

Request (MCP action `create_pr`):

{
  "action": "create_pr",
  "payload": {
    "title": "Short summary",
    "body": "Detailed PR description",
    "head_branch": "feature/xyz",
    "base_branch": "main",
    "draft": false,
    "reviewers": ["alice","bob"],
    "labels": ["autogen","feature"]
  },
  "dry_run": false
}

Success Response:

{
  "status": "created",
  "pr_number": 42,
  "pr_url": "https://github.com/owner/repo/pull/42"
}

Error Response:

{
  "status": "error",
  "errors": ["missing_permission", "rate_limited"]
}

Guidance

- Agents should validate the request payload before issuing MCP calls.
- Use `dry_run: true` for safe end-to-end tests; the service should return a simulated `pr_url` or explicit dry-run indicator.
- The orchestrator must gate on `status: created` and `pr_url` presence before proceeding.
- If MCP is unavailable, agents should provide a clear CLI fallback in their output explaining how to run `gh pr create` manually.

Authentication & Scopes

- Document required GitHub token scopes (minimum: `repo` to create pull requests; add `workflow` if the PR must trigger workflows).
- Store credentials per project Copilot/MCP configuration; do not hardcode secrets in agent files.

Examples

Include a short example of a `create_pr` request and expected response (see above). Use the skill file as the canonical reference for implementations.
