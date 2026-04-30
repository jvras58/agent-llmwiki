from agentscope.agent import ReActAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.model import OllamaChatModel
from agentscope.tool import Toolkit

from nexus.prompts import build_system_prompt
from nexus.settings import NexusSettings
from nexus.tools.registry import register_default_tools


def build_nexus_agent(settings: NexusSettings) -> ReActAgent:
    """Constrói e devolve um ReActAgent configurado conforme NexusSettings.

    Sem efeitos colaterais — não inicia loop nem rede; apenas instancia
    o modelo, o toolkit e o agente.
    """
    model_kwargs: dict[str, object] = {"model_name": settings.model_name}
    if settings.ollama_host:
        model_kwargs["host"] = settings.ollama_host

    model = OllamaChatModel(**model_kwargs)
    formatter = OllamaChatFormatter()

    toolkit = Toolkit()
    register_default_tools(toolkit, settings)

    return ReActAgent(
        name="Nexus",
        sys_prompt=build_system_prompt(settings),
        model=model,
        formatter=formatter,
        toolkit=toolkit,
        max_iters=settings.max_iters,
    )
