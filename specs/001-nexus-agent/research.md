# Research: Agente Nexus — LLM-Wiki

**Branch**: `001-nexus-agent` | **Date**: 2026-04-29
**Phase**: 0 — Outline & Research

---

## 1. AgentScope: ReActAgent + ServiceToolkit Pattern

**Decision**: Use `agentscope.agents.ReActAgent` with `agentscope.service.ServiceToolkit`.

**Rationale**: ReActAgent implements the Thought → Action → Observation loop natively.
`ServiceToolkit.add(fn)` registers any Python callable as a tool — the function docstring
becomes the tool description surfaced to the LLM. This maps directly to `read_vault` and
`update_memory`.

**Key API facts**:
- `toolkit = ServiceToolkit(); toolkit.add(read_vault); toolkit.add(update_memory)`
- `agentscope.init(model_configs=[...])` must be called before instantiating agents
- `ReActAgent(name, model_config_name, sys_prompt, service_toolkit, max_iters=3)`
- `UserAgent(name="User")` provides the conversational counterpart

**Alternatives considered**:
- Raw LLM + manual function-call parsing: rejected — too much boilerplate
- LangChain/LangGraph: rejected — constitution mandates AgentScope

---

## 2. Ollama / Llama 3 Configuration in AgentScope

**Decision**: Use AgentScope's built-in `ollama_chat` model type.

**Rationale**: AgentScope supports Ollama out of the box. The model config dict is passed
to `agentscope.init()` and referenced by name when instantiating agents.

**Configuration**:
```python
model_config = {
    "config_name": "ollama_nexus",
    "model_type": "ollama_chat",
    "model_name": "llama3",
}
```

**Prerequisites**: Ollama must be running locally (`ollama serve`) and `llama3` pulled
(`ollama pull llama3`) before the agent starts.

**Alternatives considered**:
- OpenAI-compatible Ollama endpoint: available but requires more config; native type is simpler
- Other local models (Mistral, Phi): out of scope; llama3 is explicitly specified

---

## 3. Pathlib Sandbox Pattern for Directory Isolation

**Decision**: Use `pathlib.Path.resolve()` to canonicalize paths, then assert the resolved
path starts with the resolved vault root.

**Rationale**: `Path.resolve()` collapses `..` segments and symlinks, preventing traversal.
Comparing `.parts` or using `.is_relative_to()` (Python 3.9+) gives a safe, readable check.

**Pattern** (Python 3.14):
```python
from pathlib import Path

VAULT_PATH = Path("./meu_vault").resolve()

def _safe_path(relative: str) -> Path:
    target = (VAULT_PATH / relative).resolve()
    if not target.is_relative_to(VAULT_PATH):
        raise ValueError(f"Path '{relative}' escapes vault boundary.")
    return target
```

**Edge cases handled**:
- `../../etc/passwd` → resolved path is outside VAULT_PATH → ValueError → error string
- `docs/../memoria/historico.md` → resolves correctly within vault → allowed
- Absolute paths passed by caller → resolve() normalizes them; boundary check catches escapes

**Alternatives considered**:
- String prefix check (`str(target).startswith(str(vault))`): fragile with trailing slashes
- OS-level chroot: over-engineered for single-user local tool

---

## 4. uv Project Initialization

**Decision**: `uv init --package nexus` to create a `src/`-layout package.

**Rationale**: `uv init --package` sets up `pyproject.toml` with `[tool.uv]` sections,
`src/nexus/__init__.py`, and a `uv.lock`. Python 3.14 is pinned via `.python-version`
or `requires-python = ">=3.14"` in `pyproject.toml`.

**Commands**:
```bash
uv init --package nexus
uv add agentscope
uv lock
```

**pyproject.toml additions**:
```toml
[project]
name = "nexus"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = ["agentscope"]
```

**Alternatives considered**:
- `uv init` (app layout): would work but `--package` gives cleaner importable structure
- poetry/pip: rejected by constitution

---

## 5. Msghub Interaction Loop

**Decision**: Use `agentscope.msghub.Msghub` as context manager around the agent loop.

**Rationale**: Msghub routes messages between participants automatically. The loop reads
user input via `UserAgent.__call__()`, passes to `ReActAgent.__call__()`, and exits on
sentinel words (`"sair"`, `"exit"`).

**Pattern**:
```python
from agentscope.msghub import Msghub

with Msghub(participants=[agente_nexus, usuario]) as hub:
    while True:
        msg = usuario()
        if msg.content.lower() in {"sair", "exit", "quit"}:
            break
        agente_nexus(msg)
```

**Alternatives considered**:
- Manual message passing without Msghub: works but loses broadcast routing
- Async event loop: not needed for single-user synchronous CLI

---

## Summary of Resolved Unknowns

| Unknown | Resolution |
|---------|------------|
| AgentScope tool registration API | `ServiceToolkit.add(fn)` with docstring as description |
| Ollama config in AgentScope | `model_type: "ollama_chat"`, `model_name: "llama3"` |
| Path sandbox implementation | `pathlib.Path.resolve()` + `Path.is_relative_to()` |
| Project init command | `uv init --package nexus` |
| Interaction loop pattern | `Msghub` context manager with `UserAgent` + `ReActAgent` |
