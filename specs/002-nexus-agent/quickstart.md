# Quickstart: Agente Nexus — LLM-Wiki

**Branch**: `002-nexus-agent` | **Date**: 2026-04-29

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.14+ | Runtime (managed by uv) |
| uv (Astral) | latest | Package and environment manager |
| Ollama | latest | Local LLM server |
| llama3 model | — | Language model (`ollama pull llama3`) |

---

## 1. Initialize the Project

```bash
# From repository root
uv init --package nexus
uv add agentscope
uv lock
```

This creates `pyproject.toml`, `uv.lock`, and `src/nexus/__init__.py`.

Verify Python version in `pyproject.toml`:
```toml
[project]
requires-python = ">=3.14"
```

---

## 2. Create the Source Files

Create the following structure under `src/nexus/`:

```
src/nexus/
├── __init__.py
├── config.py        # VAULT_PATH, model config
├── main.py          # entry point + Msghub loop
└── tools/
    ├── __init__.py
    └── vault.py     # read_vault, update_memory
```

Refer to `contracts/vault-tools.md` for the exact signatures and docstrings required.

---

## 3. Create the Vault

```bash
mkdir -p meu_vault/docs
mkdir -p meu_vault/memoria
```

Author `meu_vault/docs/perfil.md` with the agent's identity. Example:
```markdown
# Nexus

**Nome:** Nexus
**Criador:** [your name]
**Função:** Agente inteligente baseado na arquitetura LLM-Wiki. Utilizo arquivos
Markdown locais do Obsidian como minha única fonte de verdade.
```

`meu_vault/memoria/historico.md` is created automatically on the first memory write.

---

## 4. Start Ollama with Llama 3

```bash
# In a separate terminal
ollama serve

# Pull the model if not already downloaded
ollama pull llama3
```

Verify Ollama is running: `curl http://localhost:11434/api/tags`

---

## 5. Run the Agent

```bash
uv run python -m nexus.main
```

You should see:
```
🤖 --- Agente Nexus Ativo (Digite 'sair' para encerrar) ---
```

---

## 6. Validation Tests

Run each scenario from `spec.md` to validate:

### Scenario 1 — Identity Query
```
You: Quem é você e quem te criou?
```
Expected: Agent calls `read_vault("docs/perfil")` and responds with content of `perfil.md`.

### Scenario 2 — Memory Write
```
You: Anota que hoje estudei AgentScope com o LLM-Wiki.
```
Expected: Agent calls `update_memory(...)`. Verify `meu_vault/memoria/historico.md` contains
a new `- Hoje estudei AgentScope com o LLM-Wiki.` entry.

### Scenario 3 — Missing File Handling
```
You: Leia o arquivo docs/inexistente
```
Expected: Agent calls `read_vault("docs/inexistente")`, receives error string, relays it to
the user without inventing content.

### Exit
```
You: sair
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ollama: command not found` | Install Ollama from https://ollama.com |
| `model "llama3" not found` | Run `ollama pull llama3` |
| `ModuleNotFoundError: agentscope` | Run `uv sync` to restore environment |
| Agent invents content | Verify tool docstrings match contract; check `max_iters` is ≥ 1 |
| `PermissionError` on vault | Check directory permissions on `meu_vault/` |
