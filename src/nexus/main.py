import ast
import asyncio

from agentscope.agent import ReActAgent, UserAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.message import TextBlock
from agentscope.model import OllamaChatModel
from agentscope.pipeline import MsgHub
from agentscope.tool import Toolkit, ToolResponse

from nexus.tools.vault import read_vault as _read_vault
from nexus.tools.vault import update_memory as _update_memory

_SYS_PROMPT = """
Você é o Nexus, um agente inteligente operando via arquitetura LLM-Wiki.
Toda a sua identidade e memória residem exclusivamente em arquivos Markdown locais
de um Vault do Obsidian. Você nunca inventa ou infere informações fora do Vault.

Regras de Operação (OBRIGATÓRIAS):

1. IDENTIDADE: Se perguntarem quem você é, quem te criou ou qual sua função,
   use OBRIGATORIAMENTE a ferramenta read_vault com o argumento 'docs/perfil'.
   Jamais responda perguntas de identidade sem antes consultar esse arquivo.

2. MEMÓRIA: Se o usuário pedir para você anotar, lembrar, registrar ou guardar
   qualquer informação, use OBRIGATORIAMENTE a ferramenta update_memory.
   Isso inclui memórias pessoais E logs de aprendizado (ex.: "anota que estudei X").

3. INTEGRIDADE — REGRA ABSOLUTA: Quando uma ferramenta retornar uma string que
   começa com 'Erro:', repasse essa mensagem exatamente ao usuário. NUNCA
   substitua, suplementa ou invente conteúdo para preencher a ausência de um arquivo.
   Um erro de leitura deve ser comunicado, não contornado com suposições.

4. RESPOSTA FINAL — REGRA ABSOLUTA: Após receber o resultado de uma ferramenta,
   você DEVE responder ao usuário em linguagem natural, em português, em prosa.
   NUNCA produza JSON, chamadas de função, código ou qualquer estrutura técnica
   na sua resposta final. Use o conteúdo retornado pela ferramenta para compor
   uma resposta clara e direta. Se já tem a informação necessária, responda
   imediatamente sem chamar mais ferramentas.
""".strip()

_SENTINELS = {"sair", "exit", "quit", "bye"}


def _extract_str(val: object) -> str:
    """Normalize tool arguments from llama3.2 marshaling quirks.

    Handles three observed formats:
      1. Plain string:                "docs/perfil"
      2. JSON schema dict:            {"type": "string", "value": "docs/perfil"}
      3. Stringified Python dict:     "{'path': 'docs/perfil'}"
    """
    if isinstance(val, dict):
        return str(val.get("value", val.get("text", next(iter(val.values()), ""))))
    if isinstance(val, str):
        stripped = val.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                parsed = ast.literal_eval(stripped)
                if isinstance(parsed, dict):
                    return str(next(iter(parsed.values()), val))
            except (ValueError, SyntaxError):
                pass
    return str(val)


def _text_response(text: str) -> ToolResponse:
    return ToolResponse(content=[TextBlock(type="text", text=text)])


def read_vault(path: str) -> ToolResponse:
    """
    Lê arquivos do vault do Obsidian.
    Uso sugerido: 'docs/perfil' para identidade, 'memoria/historico' para histórico.
    Retorna o conteúdo do arquivo como texto ou uma mensagem de erro clara.
    """
    return _text_response(_read_vault(_extract_str(path)))


def update_memory(content: str) -> ToolResponse:
    """
    Adiciona uma nova linha à memória do agente no arquivo memoria/historico.md.
    Use sempre que o usuário pedir para anotar, lembrar ou registrar algo importante.
    O conteúdo é adicionado como um bullet point Markdown.
    """
    return _text_response(_update_memory(_extract_str(content)))


async def _run() -> None:
    model = OllamaChatModel(model_name="llama3.2")
    formatter = OllamaChatFormatter()

    toolkit = Toolkit()
    toolkit.register_tool_function(read_vault, func_name="read_vault")
    toolkit.register_tool_function(update_memory, func_name="update_memory")

    nexus = ReActAgent(
        name="Nexus",
        sys_prompt=_SYS_PROMPT,
        model=model,
        formatter=formatter,
        toolkit=toolkit,
        max_iters=5,
    )
    user = UserAgent(name="User")

    print("\n🤖 --- Agente Nexus Ativo (Digite 'sair' para encerrar) ---\n")

    async with MsgHub(participants=[nexus, user]):
        while True:
            msg = await user()
            if isinstance(msg.content, str) and msg.content.strip().lower() in _SENTINELS:
                print("Encerrando o Nexus. Até logo!")
                break
            await nexus(msg)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
