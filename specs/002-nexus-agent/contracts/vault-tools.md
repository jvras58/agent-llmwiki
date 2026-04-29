# Contract: Vault Tool Functions

**Branch**: `002-nexus-agent` | **Date**: 2026-04-29
**Phase**: 1 — Design & Contracts
**Module**: `src/nexus/tools/vault.py`

These are the two tool functions registered in the AgentScope `ServiceToolkit`. Their
signatures and docstrings are the contract the LLM sees when deciding which tool to call.

---

## `read_vault(path: str) -> str`

**Purpose**: Read a Markdown file from within the vault sandbox and return its text content.

**Signature**:
```
read_vault(path: str) -> str
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | Relative path within the vault, without `.md` extension (e.g., `"docs/perfil"`, `"memoria/historico"`). |

**Return values**:

| Condition | Return value |
|-----------|-------------|
| File exists and is readable | Full UTF-8 text content of the file |
| File does not exist | `"Erro: Documento '{path}.md' não encontrado no vault."` |
| Path escapes vault boundary | `"Erro: Acesso negado. O caminho '{path}' está fora do vault."` |
| Any other I/O error | `"Erro de I/O ao ler '{path}': {exception message}"` |

**Invariants**:
- NEVER raises an exception to the caller — all errors become return strings.
- NEVER reads from a path outside `VAULT_PATH`.
- Appends `.md` extension automatically.

**Docstring (LLM-visible)**:
```
Lê arquivos do vault do Obsidian.
Uso sugerido: 'docs/perfil' para identidade, 'memoria/historico' para histórico.
Retorna o conteúdo do arquivo como texto ou uma mensagem de erro clara.
```

---

## `update_memory(content: str) -> str`

**Purpose**: Append a new bullet-point entry to the memory log file.

**Signature**:
```
update_memory(content: str) -> str
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | `str` | The text of the memory entry to record (without the `- ` prefix). |

**Return values**:

| Condition | Return value |
|-----------|-------------|
| Write succeeds | `"Memória atualizada com sucesso."` |
| Write fails (permissions, disk full) | `"Erro ao escrever memória: {exception message}"` |

**Invariants**:
- NEVER modifies, deletes, or overwrites existing content in `memoria/historico.md`.
- Opens file in append mode (`"a"`) exclusively.
- Creates `memoria/historico.md` and parent directories if they do not exist.
- Writes `\n- {content}` (newline then bullet prefix) to ensure entries are on separate lines.
- NEVER raises an exception to the caller — all errors become return strings.
- Target path is always `VAULT_PATH / "memoria" / "historico.md"` — callers cannot redirect it.

**Docstring (LLM-visible)**:
```
Adiciona uma nova linha à memória do agente no arquivo memoria/historico.md.
Use sempre que o usuário pedir para anotar, lembrar ou registrar algo importante.
O conteúdo é adicionado como um bullet point Markdown.
```

---

## Shared Invariants

- Both functions import `VAULT_PATH` from `nexus.config`.
- Both functions use `pathlib.Path` exclusively for path manipulation.
- Sandbox validation (`_safe_path`) is applied before any file system call.
- UTF-8 encoding is used for all reads and writes.
