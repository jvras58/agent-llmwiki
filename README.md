# Nexus — Agente LLM-Wiki

Nexus é um agente de IA local baseado na arquitetura **LLM-Wiki**: em vez de um banco vetorial (RAG), toda a identidade e memória do agente vivem em arquivos Markdown de um Vault do Obsidian. O LLM nunca inventa — se não está no Vault, não sabe.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        Usuário (terminal)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ pergunta / comando
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentScope MsgHub                         │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │               ReActAgent "Nexus"                    │   │
│   │                                                     │   │
│   │  sys_prompt  ─────►  llama3.2 (via Ollama local)   │   │
│   │                           │                         │   │
│   │                    decide tool call                 │   │
│   │                           │                         │   │
│   │              ┌────────────┴────────────┐            │   │
│   │              ▼                         ▼            │   │
│   │        read_vault               update_memory       │   │
│   │              │                         │            │   │
│   └──────────────┼─────────────────────────┼────────────┘   │
└──────────────────┼─────────────────────────┼────────────────┘
                   │                         │
                   ▼                         ▼
        ┌──────────────────┐     ┌──────────────────────┐
        │  meu_vault/      │     │  meu_vault/          │
        │  docs/perfil.md  │     │  memoria/historico.md│
        │  (identidade)    │     │  (append-only)       │
        └──────────────────┘     └──────────────────────┘
```

### Princípios da arquitetura LLM-Wiki

| Conceito | RAG tradicional | LLM-Wiki (este projeto) |
|---|---|---|
| Fonte da verdade | Banco vetorial + embeddings | Arquivos Markdown locais |
| Atualização de memória | Re-indexação | Append direto no arquivo |
| Identidade do agente | System prompt hardcoded | Lida do Vault em tempo real |
| Inferência sem dados | Possível (alucinação) | Proibida por regra absoluta |
| Dependência externa | API de embedding | Nenhuma (tudo local) |

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.14 |
| Gerenciador de pacotes | [uv](https://docs.astral.sh/uv/) (Astral) |
| Framework de agentes | [AgentScope](https://github.com/modelscope/agentscope) 1.0.19+ |
| Modelo de linguagem | llama3.2 via [Ollama](https://ollama.com/) (local) |
| Vault / memória | Obsidian Markdown (`meu_vault/`) |
| Segurança de I/O | `pathlib` + `Path.is_relative_to()` (sandbox de diretório) |

---

## Estrutura do projeto

```
agent-llmwiki/
├── src/nexus/
│   ├── main.py          # Entry point: MsgHub loop, ReActAgent, Toolkit
│   ├── config.py        # VAULT_PATH resolvido de ./meu_vault
│   └── tools/
│       └── vault.py     # read_vault(), update_memory(), _safe_path()
├── meu_vault/
│   ├── docs/
│   │   └── perfil.md    # Identidade do Nexus (somente leitura pelo agente)
│   └── memoria/
│       └── historico.md # Log append-only de memórias e aprendizados
├── specs/
│   └── 002-nexus-agent/ # Especificação completa (Speckit workflow)
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── ...
├── pyproject.toml
└── uv.lock
```

---

## Pré-requisitos

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — gerenciador de dependências
- **[Ollama](https://ollama.com/download)** — runtime do modelo local

```bash
# Instalar o modelo
ollama pull llama3.2
```

---

## Como rodar

```bash
# 1. Clonar o repositório
git clone https://github.com/jvras58/agent-llmwiki.git
cd agent-llmwiki

# 2. Instalar dependências (uv cria o venv automaticamente)
uv sync

# 3. Garantir que o Ollama está rodando
ollama serve   # em outro terminal, se ainda não estiver ativo

# 4. Iniciar o agente
uv run nexus
```

O agente abre um loop interativo no terminal:

```
🤖 --- Agente Nexus Ativo (Digite 'sair' para encerrar) ---

User: Quem é você?
Nexus: [lê docs/perfil.md e responde em prosa]

User: Anota que hoje estudei AgentScope
Nexus: [grava em memoria/historico.md e confirma]

User: sair
Encerrando o Nexus. Até logo!
```

---

## User Stories implementadas

| ID | Cenário | Como testar |
|---|---|---|
| US1 | Consulta de identidade | Pergunte "Quem é você?" — resposta vem exclusivamente de `docs/perfil.md` |
| US2 | Escrita de memória | "Anota que estudei X" — nova linha aparece em `memoria/historico.md` |
| US3 | Arquivo inexistente | "Leia docs/inexistente" — agente retorna o erro exato da ferramenta, sem inventar |

---

## Segurança

- **Sandbox de diretório:** `_safe_path()` resolve o caminho e verifica `Path.is_relative_to(VAULT_PATH)` antes de qualquer I/O. Tentativas de path traversal (`../../etc/passwd`) são bloqueadas e retornam erro.
- **Memória append-only:** `update_memory()` abre o arquivo em modo `"a"` — entradas anteriores nunca são modificadas.
- **Zero inferência externa:** o system prompt proíbe explicitamente que o agente invente informações quando uma ferramenta retorna erro.

---

## Customizar o Vault

Edite os arquivos em `meu_vault/` diretamente no Obsidian ou em qualquer editor de texto. O agente sempre lê o estado atual do disco — sem re-indexação necessária.

Para adicionar novos documentos acessíveis ao agente, basta criar arquivos `.md` dentro de `meu_vault/` e pedir ao Nexus `leia docs/meu-arquivo`.
