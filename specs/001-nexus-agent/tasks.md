---

description: "Task list for Agente Nexus — LLM-Wiki implementation"
---

# Tasks: Agente Nexus — LLM-Wiki com Identidade, Memória e Resiliência de I/O

**Input**: Design documents from `specs/001-nexus-agent/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/vault-tools.md ✅

**Tests**: Not requested — no test tasks generated.

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All file paths are relative to repository root

## Path Conventions

- Source: `src/nexus/` (uv `--package` layout)
- Vault: `meu_vault/` (runtime knowledge base)
- All vault paths resolve relative to `VAULT_PATH = Path("./meu_vault").resolve()`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — creates the skeleton before any user story work begins.

- [x] T001 Initialize uv project: run `uv init --package nexus` in repository root (creates `pyproject.toml`, `uv.lock`, `src/nexus/__init__.py`)
- [x] T00X [P] Add agentscope dependency and lock: run `uv add agentscope && uv lock` — commit `uv.lock`
- [x] T00X [P] Create vault directory structure: `meu_vault/docs/` and `meu_vault/memoria/` (these directories must exist at agent startup per spec Assumptions)
- [x] T00X [P] Author `meu_vault/docs/perfil.md` with agent identity content: name (Nexus), creator, and function description — this file is read-only from the agent's perspective

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on before any story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T00X Create `src/nexus/config.py` — define `VAULT_PATH = Path("./meu_vault").resolve()` and `MODEL_CONFIG` dict (`config_name: "ollama_nexus"`, `model_type: "ollama_chat"`, `model_name: "llama3"`)
- [x] T00X [P] Create `src/nexus/tools/__init__.py` (empty package marker)
- [x] T00X Implement `_safe_path(relative: str) -> pathlib.Path` in `src/nexus/tools/vault.py` — resolves `VAULT_PATH / relative`, asserts `Path.is_relative_to(VAULT_PATH)`; raises `ValueError` with user-readable message on boundary violation; this function is the sandbox gate called by both vault tools

**Checkpoint**: Foundation ready — VAULT_PATH resolves correctly and _safe_path blocks `../../` traversal.

---

## Phase 3: User Story 1 — Consulta de Identidade (Priority: P1) 🎯 MVP

**Goal**: Agent reads `docs/perfil.md` from the vault and answers identity queries using
only the file's content — zero inferred or invented facts.

**Independent Test**: Run agent, ask "Quem é você?" — verify the response traces exclusively
to `meu_vault/docs/perfil.md` content. Delete the file and ask again — agent must return an
error message, not fabricated identity.

### Implementation for User Story 1

- [x] T00X [US1] Implement `read_vault(path: str) -> str` in `src/nexus/tools/vault.py` — calls `_safe_path`, opens file in UTF-8 read mode, returns content; catches `ValueError` (traversal), `FileNotFoundError`, `PermissionError`, and `OSError` and returns human-readable error strings per `contracts/vault-tools.md`; include the LLM-visible docstring exactly as specified in the contract
- [x] T00X [US1] Create `src/nexus/main.py` — call `agentscope.init(model_configs=[MODEL_CONFIG])`, create `ServiceToolkit`, register `read_vault` via `toolkit.add(read_vault)`
- [x] T010 [US1] Instantiate `ReActAgent("Nexus", ...)` with `sys_prompt` containing identity rule (consult `read_vault("docs/perfil")` for all identity queries, never guess); add `UserAgent("User")`; implement `Msghub` loop with sentinel exit (`"sair"`, `"exit"`); expose `main()` function entry point in `src/nexus/main.py`

**Checkpoint**: User Story 1 fully functional — agent answers "Quem é você?" from vault only.

---

## Phase 4: User Story 2 — Escrita de Memórias e Logs de Aprendizado (Priority: P2)

**Goal**: Agent appends new bullet-point entries to `memoria/historico.md` on user request.
Prior entries are never modified. File is created on first write if absent.

**Independent Test**: Ask agent "Anota que hoje estudei AgentScope". Verify
`meu_vault/memoria/historico.md` gains a new `- ...` line. Restart session and verify entry
persists with all prior entries intact.

### Implementation for User Story 2

- [x] T011 [US2] Implement `update_memory(content: str) -> str` in `src/nexus/tools/vault.py` — target is always `VAULT_PATH / "memoria" / "historico.md"`; creates parent dirs if absent (`mkdir(parents=True, exist_ok=True)`); opens in append mode `"a"` (UTF-8); writes `f"\n- {content}"`; catches `PermissionError` and `OSError` and returns error strings; include the LLM-visible docstring per contract
- [x] T012 [US2] Register `update_memory` in `ServiceToolkit` via `toolkit.add(update_memory)` in `src/nexus/main.py` (add alongside existing `read_vault` registration from T009)
- [x] T013 [US2] Extend `sys_prompt` in `src/nexus/main.py` with memory-write rule: use `update_memory` whenever the user asks to remember, note, annotate, or log something; both memories and learning-log entries use the same tool

**Checkpoint**: User Stories 1 AND 2 independently functional. Memory entries survive session restarts.

---

## Phase 5: User Story 3 — Tratamento de Arquivos Inexistentes (Priority: P3)

**Goal**: When a vault file does not exist or a path traversal is attempted, the agent
relays the tool's error string to the user without supplementing, guessing, or inventing
what the file might have contained.

**Independent Test**: Ask agent to read `docs/inexistente`. Verify the response contains
the error string from `read_vault` and zero fabricated content.

### Implementation for User Story 3

- [x] T014 [US3] Extend `sys_prompt` in `src/nexus/main.py` with anti-hallucination/error-relay rule: when a tool returns a string beginning with "Erro:", relay it verbatim to the user; never supplement, infer, or invent content to replace a missing file; this rule MUST be stated explicitly so the LLM treats error strings as terminal, not as prompts to guess

**Checkpoint**: All three user stories independently functional. Asking for a missing file produces only the error message.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final wiring, entry point registration, and end-to-end validation.

- [x] T015 [P] Add console entry point to `pyproject.toml`: `[project.scripts] nexus = "nexus.main:main"` — enables `uv run nexus` as the launch command
- [x] T016 Run end-to-end validation against all three quickstart.md scenarios: identity query (SC-001/002), memory write and retrieval (SC-003), missing file error relay (SC-004), and path traversal block (SC-005)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 (specifically T007 for _safe_path)
- **US2 (Phase 4)**: Depends on Phase 2 (T007) AND Phase 3 (T009 for toolkit/main.py)
- **US3 (Phase 5)**: Depends on Phase 3 (T008 read_vault handles error paths) AND Phase 4 complete (full sys_prompt context)
- **Polish (Phase 6)**: Depends on Phase 5 completion

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependency on US2/US3
- **US2 (P2)**: Can start after US1 Phase 3 completes (shares main.py and ServiceToolkit)
- **US3 (P3)**: Behavioral — error handling already in T008; only sys_prompt extension needed after US2

### Within Each User Story

- Models/tools before services before agent wiring
- `_safe_path` (T007) before `read_vault` (T008) before `update_memory` (T011)
- `agentscope.init` before `ReActAgent` instantiation
- `ServiceToolkit` registration before `ReActAgent` creation

### Parallel Opportunities

- T002, T003, T004 can all run in parallel with each other after T001
- T006 can run in parallel with T005
- T015 can run in parallel with T016 preparation

---

## Parallel Example: Phase 1 Setup

```bash
# After T001 completes (uv init):
Task: "uv add agentscope && uv lock"          # T002
Task: "mkdir -p meu_vault/docs meu_vault/memoria"  # T003
Task: "Author meu_vault/docs/perfil.md"        # T004
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T007) — CRITICAL blocker
3. Complete Phase 3: US1 (T008–T010)
4. **STOP and VALIDATE**: Ask "Quem é você?" — confirm response from vault only
5. Agent is usable for identity queries — deployable MVP

### Incremental Delivery

1. T001–T007 → Foundation ready
2. T008–T010 → US1 complete: identity queries work ✅
3. T011–T013 → US2 complete: memory writes work ✅
4. T014 → US3 complete: error relay guaranteed ✅
5. T015–T016 → Polish and validate all scenarios ✅

---

## Notes

- `[P]` tasks operate on different files and have no incomplete dependencies
- `[US?]` label maps each task to a specific user story for traceability
- No test tasks generated (not requested in spec)
- `update_memory` target path is hardcoded — callers cannot redirect it (security invariant)
- `_safe_path` is not registered as a tool — it is an internal helper only
- Commit `uv.lock` after T002 to ensure reproducible installs
