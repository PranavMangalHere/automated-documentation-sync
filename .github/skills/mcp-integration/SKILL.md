# MCP Integration Skill

Purpose

This skill documents the GitHub MCP contract used by the pipeline to create pull requests. It standardizes the tool arguments, normalized response, error handling, and approval gate used by the PR agent and orchestrator.

Contract

Request (GitHub MCP tool `create_pull_request`):

{
  "owner": "owner",
  "repo": "repository",
  "title": "Short summary",
  "body": "Detailed PR description",
  "head": "feature/xyz",
  "base": "main",
  "draft": false,
  "maintainer_can_modify": true,
  "reviewers": ["alice", "bob"]
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

- The PR agent must validate direct tool arguments before issuing the MCP call.
- `create_pull_request` has no dry-run argument. The L3 explicit-approval gate is the required safeguard before calling it.
- The orchestrator must gate on `status: created` and `pr_url` presence before proceeding.
- If MCP is unavailable, agents should provide a clear CLI fallback in their output explaining how to run `gh pr create` manually.

Authentication & Scopes

- GitHub MCP uses the authenticated GitHub account configured for the `github` MCP server; do not hardcode credentials or tokens.
- That account must have permission to open pull requests in the target repository. Repository rules or organization policy can still deny the request.
- The CLI fallback requires separately authenticated `gh` credentials with equivalent repository access.

Examples

Include a short example of a `create_pull_request` request and expected response (see above). Use the skill file as the canonical reference for implementations.
