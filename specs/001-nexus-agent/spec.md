# Feature Specification: Agente Nexus — LLM-Wiki com Identidade, Memória e Resiliência de I/O

**Feature Branch**: `001-nexus-agent`
**Created**: 2026-04-29
**Status**: Draft
**Input**: User description: "Construir o Agente Nexus baseado na arquitetura LLM-Wiki usando Python."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulta de Identidade (Priority: P1)

A user asks the Nexus Agent who it is, who created it, or what its function is. The agent
MUST read `docs/perfil.md` from the vault before formulating any response. No identity
information may be inferred, assumed, or invented — the file is the sole authority.

**Why this priority**: Identity trust is the foundation of every other interaction. An agent
that guesses at its own description erodes user confidence and violates the core LLM-Wiki
contract.

**Independent Test**: Ask "Who are you?" with a populated `docs/perfil.md` and verify the
response traces exclusively to that file's content. Then delete the file and ask again —
the agent must return an error, not a fabricated identity.

**Acceptance Scenarios**:

1. **Given** `docs/perfil.md` exists with agent name, creator, and purpose,
   **When** the user asks "Who are you and what can you do?",
   **Then** the agent's response contains only information found in that file — zero
   inferred or invented content.

2. **Given** `docs/perfil.md` does not exist,
   **When** the user asks any identity question,
   **Then** the agent returns a clear, user-friendly error message stating the profile
   file was not found, and provides no fabricated identity content.

---

### User Story 2 - Escrita de Memórias e Logs de Aprendizado (Priority: P2)

A user shares a fact, observation, or learning they want the agent to retain. The agent
MUST append a new bullet-point line to `memoria/historico.md`. Existing entries MUST
remain intact. The operation covers both short-term memories ("remember that…") and
explicit learning logs ("note that I studied…").

**Why this priority**: Persistent, trustworthy memory is the primary value of the LLM-Wiki
architecture. If memory writes corrupt prior entries, the knowledge base becomes unreliable.

**Independent Test**: Record an entry, close and reopen a session, and verify the entry
persists in `memoria/historico.md` with all previous entries unmodified. Record a second
entry and verify both coexist.

**Acceptance Scenarios**:

1. **Given** the user says "Anota que hoje estudei AgentScope",
   **When** the agent processes the message,
   **Then** a new line `- Hoje estudei AgentScope` (or equivalent) is appended to
   `memoria/historico.md`; all previous entries remain unchanged.

2. **Given** `memoria/historico.md` does not yet exist,
   **When** the user requests any memory write,
   **Then** the file is created (including any missing parent directories) and the
   entry is written as the first line.

3. **Given** multiple memory entries have been recorded across sessions,
   **When** the user asks "What have you noted about me?",
   **Then** the agent reads `memoria/historico.md` and summarizes its contents without
   adding any information not present in the file.

---

### User Story 3 - Tratamento de Arquivos Inexistentes (Priority: P3)

A user or the agent's reasoning process attempts to read a vault file that does not exist.
The file-access operation MUST detect the absence and return a human-readable error string.
The agent MUST relay this error to the user without inferring, fabricating, or guessing
what the file might have contained.

**Why this priority**: Graceful I/O failure is the last line of defense against hallucination.
If missing-file reads silently return empty strings or exceptions are swallowed, the agent
may proceed to invent content.

**Independent Test**: Issue a read request for a known non-existent vault path (e.g.,
`docs/inexistente.md`). Verify the agent returns an identifiable error message and zero
fabricated content in the same response turn.

**Acceptance Scenarios**:

1. **Given** a vault file does not exist at the requested path,
   **When** the agent's tool attempts to read it,
   **Then** the tool returns a clear error string (e.g., "Erro: Documento não encontrado."),
   and the agent relays this to the user without supplementing with invented content.

2. **Given** a read attempt targets a path outside `meu_vault/` (e.g., a path with `../../`),
   **When** the tool validates the path,
   **Then** the request is blocked before any file system access and the agent informs the
   user that the requested path is outside the permitted vault boundary.

---

### Edge Cases

- What happens if `docs/perfil.md` exists but is empty or contains only whitespace?
- What happens if a write to `memoria/historico.md` fails due to a disk-full or permissions error?
- What happens if the vault root directory `meu_vault/` itself does not exist at startup?
- What happens if a path traversal sequence is embedded mid-path (e.g., `docs/../../../etc`)?
- What happens if `memoria/historico.md` grows to a very large size over extended use?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The agent MUST retrieve identity information exclusively by reading
  `docs/perfil.md`; it MUST NOT use any other data source or internal assumption for
  self-description.
- **FR-002**: The agent MUST append memory and learning-log entries to `memoria/historico.md`
  using the Markdown bullet-point prefix `- `.
- **FR-003**: Memory append operations MUST NEVER delete, overwrite, or modify any
  previously written entry in `memoria/historico.md`.
- **FR-004**: If `memoria/historico.md` does not exist at write time, the system MUST
  create the file (and any missing parent directories) before appending.
- **FR-005**: All vault file-read operations MUST return a human-readable error string
  when the target file does not exist, so the agent can relay the error to the user.
- **FR-006**: The agent MUST NOT infer, guess, or synthesize any information that is
  not explicitly present in a vault file read at runtime.
- **FR-007**: All file-access operations MUST be restricted to paths within `meu_vault/`;
  paths that resolve outside this boundary (including traversal sequences) MUST be
  rejected before any file system access occurs.

### Key Entities

- **Vault** (`meu_vault/`): Root directory for all agent knowledge. Defines the permitted
  I/O sandbox. All file paths are interpreted relative to this root.
- **Profile** (`meu_vault/docs/perfil.md`): Markdown file containing the agent's name,
  creator, and functional description. Treated as read-only by the agent.
- **Memory Log** (`meu_vault/memoria/historico.md`): Append-only Markdown file recording
  facts, events, and learning entries accumulated across sessions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of identity queries where `docs/perfil.md` exists, the agent
  response is derived solely from that file — zero inferred or invented facts.
- **SC-002**: In 100% of identity queries where `docs/perfil.md` is absent, the agent
  returns an error message and zero fabricated identity content.
- **SC-003**: Memory and learning-log entries recorded in one session are present and
  unaltered in `memoria/historico.md` in all subsequent sessions.
- **SC-004**: Every missing-file read attempt produces a user-visible error message in
  the same response turn — the agent never silently fails or supplements with invented data.
- **SC-005**: Zero successful path traversal attempts: any access to a path outside
  `meu_vault/` is blocked at the tool layer before any file system operation executes.

## Assumptions

- The vault root `meu_vault/` exists and is accessible at the process working directory
  when the agent starts; if absent, startup SHOULD fail with a clear error.
- `docs/perfil.md` is manually authored by the operator before deployment; the agent
  never creates or modifies it.
- `memoria/historico.md` may or may not exist at first run; the agent creates it on
  demand during the first memory write.
- The agent operates in a single-user, local-only context; no concurrent write
  coordination is required for the initial version.
- Users interact with the agent through a conversational turn-by-turn text interface.
- "Memory" and "learning log" entries are treated identically at the storage layer:
  both are appended as bullet-point lines to `memoria/historico.md`.
- The agent's response language matches the user's input language by default.
