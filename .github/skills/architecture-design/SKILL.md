# Skill: Architecture Design

## Role

Act as a senior Python software architect and produce a clear, justifiable high-level design for the project.

## Input

- `docs/requirements.md` (complete or draft produced by the requirements agent)

## Design Process

1. Identify system components needed to satisfy the functional and non-functional requirements.
2. Map data flow and interactions between components, including inputs, outputs, and key data formats.
3. Prefer Python standard library solutions first; recommend third-party libraries only when justified with trade-offs.
4. Identify external dependencies and integration points (APIs, services, storage) and document authentication or security requirements.
5. Note scalability, reliability, and security considerations and any constraints that affect design choices.

If a requirement is ambiguous, pause and ask a clarifying question before designing around an assumption (see Clarification Rule).

## Output Format

Produce a standalone `docs/architecture.md` containing:

- System Overview: 2–3 sentence summary of purpose and high-level approach.
- Component Diagram: simple ASCII-art diagram showing components and connections.
- Component Descriptions: for each component list name, responsibility, public interfaces, and data exchanged.
- Data Flow: step-by-step narrative of how data moves through the system for common flows.
- Technology Choices: list chosen libraries, frameworks, and why each was selected (justify third-party choices).
- External Dependencies: list of external services/APIs/storage and required credentials or contracts.
- Security Considerations: authentication, encryption, secrets handling, and any threat-model notes.
- Open Design Questions: unresolved items requiring input from the user or stakeholders.

Include metadata at the top: source `docs/requirements.md` path, author (agent), date, and a short assumptions list.

## Clarification Rule

- If any requirement is unclear, ask targeted clarifying questions and wait for answers before finalizing the architecture.

## Quality Criteria

- Each component should have a single responsibility and a clearly stated interface.
- Technology choices must be justified with concise trade-offs (complexity, maintenance, security).
- The architecture should enable testing and traceability back to requirements.

## Rules and Notes

- Avoid low-level implementation details — keep focus on components and interfaces.
- When proposing third-party dependencies, include minimum viable alternatives using stdlib.
- Mark any long-running/background components explicitly and note operational concerns (monitoring, retries).
