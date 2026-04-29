# Data Model: Agente Nexus — LLM-Wiki

**Branch**: `002-nexus-agent` | **Date**: 2026-04-29
**Phase**: 1 — Design & Contracts

---

## Entities

### VaultPath

Represents a validated file path within the vault sandbox.

| Attribute | Type | Description |
|-----------|------|-------------|
| `raw` | `str` | Caller-supplied relative path (e.g., `"docs/perfil"`) |
| `resolved` | `pathlib.Path` | Absolute path after `Path.resolve()` |
| `is_safe` | `bool` | True if `resolved.is_relative_to(VAULT_PATH)` |

**Validation rules**:
- `raw` MUST NOT be empty.
- `resolved` MUST be a descendant of `VAULT_PATH` after resolution.
- Any path that fails validation MUST raise `ValueError` before I/O occurs.

**Note**: The `.md` extension is appended automatically by `read_vault` if the caller
omits it (e.g., `"docs/perfil"` → `docs/perfil.md`). This matches Obsidian conventions.

---

### AgentProfile

Contents of `meu_vault/docs/perfil.md`. Read-only from the agent's perspective.

| Attribute | Type | Description |
|-----------|------|-------------|
| `raw_content` | `str` | Full Markdown text of the file |
| `source_path` | `VaultPath` | Always `docs/perfil.md` |

**State transitions**:
- Does not exist → `read_vault("docs/perfil")` returns error string
- Exists → `read_vault("docs/perfil")` returns `raw_content`
- The agent NEVER writes to this entity.

---

### MemoryEntry

A single bullet-point line appended to the memory log.

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | `str` | The text of the entry (without the `- ` prefix) |
| `formatted` | `str` | `f"\n- {content}"` — the exact bytes written to disk |

**Validation rules**:
- `content` MUST NOT be empty.
- `formatted` always begins with `\n- ` to ensure entries are separated on distinct lines.

---

### MemoryLog

Represents `meu_vault/memoria/historico.md` as a whole.

| Attribute | Type | Description |
|-----------|------|-------------|
| `source_path` | `VaultPath` | Always `memoria/historico.md` |
| `entries` | `list[str]` | Lines matching `^- ` when the file is read |

**State transitions**:
- Does not exist → `update_memory(content)` creates file + parent dirs, writes first entry
- Exists → `update_memory(content)` appends `\n- {content}` without touching prior content
- Read → `read_vault("memoria/historico")` returns full file content

**Invariant**: The log is append-only. No operation ever removes or modifies an existing line.

---

## Vault Directory Layout

```text
meu_vault/                      ← VAULT_PATH root (sandbox boundary)
├── docs/
│   └── perfil.md               ← AgentProfile source (operator-authored)
└── memoria/
    └── historico.md            ← MemoryLog (auto-created on first write)
```

All paths passed to `read_vault` and `update_memory` are resolved relative to this root.
The root itself is defined as `VAULT_PATH = Path("./meu_vault").resolve()` in `config.py`.
