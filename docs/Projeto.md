# 🧠 Projeto LLM-Wiki: Integração AgentScope & Obsidian

Este documento detalha a validação e estruturação do **Agente Nexus**, baseado na arquitetura **LLM-Wiki**. O sistema utiliza arquivos locais do Obsidian como "fonte da verdade", substituindo a necessidade de sistemas complexos de RAG (Retrieval-Augmented Generation) por uma integração direta com Markdown.

---

## 📂 1. Estrutura de Pastas (Vault)

A organização do diretório garante que o agente saiba exatamente onde buscar identidades e onde registrar logs de memória.

```text
meu_vault/
├── docs/
│   └── perfil.md         # Conteúdo: Nome, criador e função do agente.
└── memoria/
    └── historico.md      # Log de eventos, fatos aprendidos e memórias.
```

---

## 💻 2. Implementação do Agente

Para garantir que o **AgentScope** execute funções Python automaticamente, utilizamos o padrão **ReActAgent** acoplado a um **ServiceToolkit**.

```py
import os
import agentscope
from agentscope.agents import ReActAgent, UserAgent
from agentscope.service import ServiceToolkit
from agentscope.msghub import Msghub

# --- 1. Configuração de Caminhos ---
VAULT_PATH = "./meu_vault"

# --- 2. Ferramentas de Acesso ao Disco (.md) ---
def read_vault(path: str) -> str:
    """
    Lê arquivos do Obsidian. 
    Uso sugerido: 'docs/perfil' ou 'memoria/historico'.
    """
    full_path = os.path.join(VAULT_PATH, f"{path}.md")
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Erro: Documento não encontrado."

def update_memory(content: str) -> str:
    """
    Adiciona uma nova linha à memória do agente no arquivo historico.md.
    """
    full_path = os.path.join(VAULT_PATH, "memoria/historico.md")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(f"\n- {content}")
    return "Memória atualizada com sucesso."

# Registro das ferramentas no Toolkit
toolkit = ServiceToolkit()
toolkit.add(read_vault)
toolkit.add(update_memory)

# --- 3. Inicialização do Modelo (Ollama) ---
model_config = {
    "config_name": "ollama_conf",
    "model_type": "ollama_chat",
    "model_name": "llama3",
}
agentscope.init(model_configs=[model_config])

# --- 4. Definição do Agente Nexus ---
prompt_sistema = """
Você é o Nexus, um Agente Inteligente operando via 'LLM-Wiki'.
Toda a sua identidade e memória residem em arquivos Markdown locais.

Regras de Operação:
1. Identidade: Se perguntarem quem você é, use 'read_vault' em 'docs/perfil'.
2. Aprendizado: Se o usuário contar algo importante, use 'update_memory'.
3. Integridade: Não invente fatos. Confie apenas nas informações do seu Vault.
"""

agente_nexus = ReActAgent(
    name="Nexus",
    model_config_name="ollama_conf",
    sys_prompt=prompt_sistema,
    service_toolkit=toolkit,
    max_iters=3
)

usuario = UserAgent(name="User")

# --- 5. Loop de Interação ---
with Msghub(participants=[agente_nexus, usuario]) as hub:
    print("\n🤖 --- Agente Nexus Ativo (Digite 'sair' para encerrar) ---")
    while True:
        msg_usuario = usuario()
        if msg_usuario.content.lower() in ["sair", "exit"]:
            break
            
        resposta = agente_nexus(msg_usuario)
```

---

## 📊 3. Análise Técnica e Validação

| Critério | Avaliação |
| :--- | :--- |
| **Substituição de RAG** | **Extremamente Eficaz.** Elimina chunking, embeddings e bancos vetoriais. Reduz a latência e evita alucinações por falta de contexto. |
| **Orquestração** | O uso de `ReActAgent` consolida a ponte LLM-Disco, permitindo um ciclo de *Pensamento -> Ação -> Observação* robusto. |
| **Privacidade e Performance** | O uso de Llama 3 via Ollama local garante a proteção de dados sensíveis e permite chamadas de I/O de alta velocidade. |

---

## 🧪 4. Roteiro de Testes Sugerido

Para validar a integração, execute os seguintes comandos no chat:

1.  **[ ] Teste de Identidade:** Pergunte *"Quem é você e quem te criou?"*.
    * *Esperado:* O log deve mostrar o agente chamando `read_vault`.
2.  **[ ] Teste de Escrita:** Diga *"Anota aí que hoje estou estudando AgentScope"*.
    * *Esperado:* Verifique se o arquivo `memoria/historico.md` foi atualizado.
3.  **[ ] Teste de Contexto:** Pergunte *"O que você tem anotado na minha memória?"*.
    * *Esperado:* O agente deve ler o histórico e sintetizar os pontos principais.

---
> **Nota:** Certifique-se de que o diretório `./meu_vault` possua permissões de leitura e escrita para o script Python.