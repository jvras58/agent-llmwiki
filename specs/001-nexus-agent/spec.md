# Feature Specification: Agente Nexus — Identidade, Memória e Resiliência

**Feature Branch**: `001-nexus-agent`
**Created**: 2026-04-29
**Status**: Draft
**Input**: User description: "Construir o Agente Nexus baseado na arquitetura LLM-Wiki."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identity Query (Priority: P1)

A user asks the Nexus Agent about its identity — who it is, who created it, or what its
purpose is. The agent MUST consult the vault file `docs/perfil.md` before responding.
Under no circumstances may the agent answer from memory or assumption.

**Why this priority**: Correct and verifiable identity is the foundation of trust in the
agent. An agent that invents facts about itself undermines all other interactions.

**Independent Test**: Ask "Who are you?" with a populated `docs/perfil.md`. Verify the
response matches only the content of that file. Then ask again with the file deleted and
verify the agent returns an error instead of an invented answer.

**Acceptance Scenarios**:

1. **Given** `docs/perfil.md` exists with agent name, creator, and function,
   **When** the user asks "Who are you?",
   **Then** the agent responds with the exact identity information from that file.

2. **Given** `docs/perfil.md` does not exist,
   **When** the user asks "Who created you?",
   **Then** the agent returns a clear error message stating the profile file was not found,
   and does NOT fabricate any identity information.

---

### User Story 2 - Memory Recording (Priority: P2)

A user shares a fact, observation, or personal note they want the agent to remember. The
agent MUST append a new bullet-point entry to `memoria/historico.md` without modifying
or deleting any previously recorded entries.

**Why this priority**: Persistent, trustworthy memory is the core value proposition of the
LLM-Wiki architecture. Overwriting history would break the integrity of the knowledge base.

**Independent Test**: Record an entry, restart the session, and verify the entry is still
present in `memoria/historico.md`. Record a second entry and verify both entries exist
and the first has not been modified.

**Acceptance Scenarios**:

1. **Given** the user says "Remember that today I studied AgentScope",
   **When** the agent processes this message,
   **Then** a new line `- Today I studied AgentScope` (or equivalent) is appended to
   `memoria/historico.md`, and all previous entries remain unchanged.

2. **Given** `memoria/historico.md` does not yet exist,
   **When** the user asks the agent to record a memory,
   **Then** the file is created and the entry is appended as the first line.

3. **Given** a memory has been recorded,
   **When** the user asks the agent to recall recorded memories,
   **Then** the agent reads `memoria/historico.md` and summarizes its contents without
   adding information that is not in the file.

---

### User Story 3 - Missing File Handling (Priority: P3)

A user requests information that would require reading a vault file that does not exist.
The agent MUST detect the absence of the file and return a clear, user-readable error
message. The agent MUST NOT invent content to fill the gap.

**Why this priority**: Graceful failure prevents the agent from producing hallucinated
content, which is the primary integrity risk of an LLM-based system.

**Independent Test**: Request information from a vault path that does not exist (e.g.,
`docs/inexistente.md`). Verify the agent responds with a recognizable error message and
that the response contains no fabricated content.

**Acceptance Scenarios**:

1. **Given** a vault file does not exist at the requested path,
   **When** the agent attempts to read it,
   **Then** the agent receives an error signal from the file-reading tool and relays a
   clear message to the user (e.g., "The document 'X' was not found in the vault.").

2. **Given** a path containing directory traversal characters (e.g., `../../etc/passwd`),
   **When** such a path is passed to a vault-reading operation,
   **Then** the operation is blocked and the agent informs the user that the path is
   outside the permitted vault boundary.

---

### Edge Cases

- What happens when `docs/perfil.md` is empty (zero bytes)?
- What happens if `memoria/historico.md` grows extremely large over time?
- How does the agent respond if a vault file exists but contains only whitespace?
- What happens if a write to `memoria/historico.md` fails due to a permissions error?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The agent MUST retrieve identity information exclusively by reading
  `docs/perfil.md` from the vault; it MUST NOT use any other source for self-description.
- **FR-002**: The agent MUST append new memory entries to `memoria/historico.md` using
  Markdown bullet-point format (`- entry text`).
- **FR-003**: Memory write operations MUST NEVER delete or modify existing entries in
  `memoria/historico.md`.
- **FR-004**: When a requested vault file does not exist, the file-access operation MUST
  return a human-readable error string that the agent can relay to the user.
- **FR-005**: The agent MUST NEVER fabricate information: all responses about identity,
  memory, or vault content MUST be grounded exclusively in file content read at runtime.
- **FR-006**: All file-access operations MUST be restricted to paths within the `meu_vault/`
  directory; paths containing traversal sequences MUST be rejected before any I/O occurs.
- **FR-007**: If `memoria/historico.md` does not exist when a write is attempted, the
  system MUST create the file (including any missing parent directories) before appending.

### Key Entities

- **Vault** (`meu_vault/`): Root directory containing all agent knowledge files. Defines
  the permitted I/O boundary. All reads and writes are relative to this root.
- **Profile** (`meu_vault/docs/perfil.md`): Markdown file holding agent identity — name,
  creator, and function description. Read-only from the agent's perspective.
- **Memory Log** (`meu_vault/memoria/historico.md`): Append-only Markdown file recording
  facts, events, and observations the agent has been asked to retain across sessions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of identity queries where `docs/perfil.md` exists, the agent
  response references only information present in that file — zero invented facts.
- **SC-002**: In 100% of identity queries where `docs/perfil.md` is absent, the agent
  returns an error message and zero fabricated identity content.
- **SC-003**: Memory entries recorded in one session are retrievable in a subsequent
  session without any prior entries having been removed or altered.
- **SC-004**: All missing-file scenarios produce a user-readable error message within the
  same response turn — the agent never silently fails or invents a substitute answer.
- **SC-005**: Zero successful path traversal attacks: any attempt to access a path outside
  `meu_vault/` is blocked at the tool layer before any file system operation occurs.

## Assumptions

- The vault directory `meu_vault/` exists and is accessible at the process working directory
  when the agent starts.
- `docs/perfil.md` is manually authored by the operator before deployment; the agent does
  not create or update it.
- `memoria/historico.md` may or may not exist at startup; the agent is responsible for
  creating it on first write.
- The agent operates in a single-user, local-only context; no concurrent write safety
  (locking) is required for the initial version.
- The user interacts with the agent through a conversational text interface (turn-by-turn).
- The agent's response language matches the user's input language by default.
