# Implementation Plan: Agente Nexus — LLM-Wiki

**Branch**: `001-nexus-agent` | **Date**: 2026-04-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-nexus-agent/spec.md`

## Summary

Build the Nexus Agent using the LLM-Wiki architecture: a ReActAgent (AgentScope) whose sole
knowledge source is a local Obsidian vault at `./meu_vault/`. Two tool functions (`read_vault`,
`update_memory`) implement sandboxed file I/O via pathlib. The agent never fabricates
information; missing files produce explicit error strings. Llama 3 runs locally via Ollama.
Project is managed with `uv init` and Python 3.14.

## Technical Context

**Language/Version**: Python 3.14
**Primary Dependencies**: agentscope, ollama (via AgentScope model backend)
**Storage**: Local Markdown files in `./meu_vault/` — no database
**Testing**: pytest (unit tests for vault tools; manual integration test per spec scenarios)
**Target Platform**: Local machine (Windows/macOS/Linux), fully offline
**Project Type**: Local CLI agent application
**Performance Goals**: Single-user local execution; interactive response latency governed by
Ollama/Llama 3 throughput — no numeric target required for v1
**Constraints**: Fully offline-capable; no external API calls; all data stays local
**Scale/Scope**: Single-user, single-session; vault grows linearly with usage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Markdown as Single Source of Truth | All identity/memory sourced from `./meu_vault/` Markdown files only | ✅ PASS |
| II. RAG Replacement (absolute) | Zero vector DBs, embeddings, or chunking — only direct file I/O | ✅ PASS |
| III. Zero Tolerance for Hallucinations | `read_vault` returns error string on missing file; agent relays error, never guesses | ✅ PASS |
| Security 1 (Directory Isolation) | `pathlib.Path.resolve()` validates all paths stay within `VAULT_PATH` | ✅ PASS |
| Security 2 (Append-Only Memory) | `update_memory` opens file in append mode (`"a"`); no truncation or overwrite | ✅ PASS |
| Security 3 (Local Privacy) | Llama 3 via Ollama — all LLM inference runs locally, zero data egress | ✅ PASS |
| Technical 1 (Python 3.14) | `uv init --python 3.14` sets the runtime | ✅ PASS |
| Technical 2 (uv) | All dependency management via uv; `uv.lock` committed | ✅ PASS |
| Technical 3 (I/O Resilience) | Both tools catch `FileNotFoundError`, `PermissionError`, `OSError` | ✅ PASS |
| Technical 4 (AgentScope) | `ReActAgent` + `ServiceToolkit`; Msghub interaction loop | ✅ PASS |

**All gates pass. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-nexus-agent/
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── vault-tools.md   # Phase 1 output — tool function contracts
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
agent-llmwiki/
├── pyproject.toml          # uv-managed project (uv init output)
├── uv.lock                 # locked dependencies (committed)
├── meu_vault/              # Obsidian vault — truth source (gitignored or committed)
│   ├── docs/
│   │   └── perfil.md       # Agent identity (operator-authored, read-only)
│   └── memoria/
│       └── historico.md    # Append-only memory log (auto-created)
└── src/
    └── nexus/
        ├── __init__.py
        ├── main.py          # Entry point — AgentScope init + Msghub loop
        ├── config.py        # VAULT_PATH constant, model config dict
        └── tools/
            ├── __init__.py
            └── vault.py     # read_vault() and update_memory() — pathlib + sandbox
```

**Structure Decision**: Single project (Option 1). No web layer, no mobile, no multi-package
monorepo. The agent is a local CLI application. All source lives under `src/nexus/` following
`uv init --package` layout conventions for Python 3.14.

## Complexity Tracking

> *No constitution violations — this section is intentionally empty.*
