import asyncio
import logging

from agentscope.agent import UserAgent
from agentscope.message import Msg
from agentscope.pipeline import MsgHub

from nexus.agents import build_nexus_agent
from nexus.schemas import NexusReply
from nexus.settings import NexusSettings, load_settings

EXIT_SENTINELS = frozenset({"sair", "exit", "quit", "bye"})

logger = logging.getLogger("nexus")


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _render_trace(reply_msg: Msg) -> None:
    """Mostra um rodapé de rastreabilidade quando o output estruturado validar."""
    metadata = getattr(reply_msg, "metadata", None)
    if not isinstance(metadata, dict):
        return
    try:
        reply = NexusReply.model_validate(metadata)
    except Exception:
        logger.debug("metadata não bateu com NexusReply: %r", metadata)
        return

    parts: list[str] = []
    if reply.sources_consulted:
        parts.append("📖 fontes: " + ", ".join(reply.sources_consulted))
    if reply.wrote_memory:
        parts.append("📝 memória atualizada")
    if parts:
        print("  └─ " + " · ".join(parts))


async def run_cli(settings: NexusSettings | None = None) -> None:
    settings = settings or load_settings()
    _configure_logging(settings.log_level)

    nexus = build_nexus_agent(settings)
    user = UserAgent(name="User")

    print("\nAgente Nexus ativo (digite 'sair' para encerrar)\n")

    async with MsgHub(participants=[nexus, user]):
        while True:
            msg = await user()
            content = msg.content
            if isinstance(content, str) and content.strip().lower() in EXIT_SENTINELS:
                print("Encerrando o Nexus. Até logo!")
                break
            reply = await nexus(msg, structured_model=NexusReply)
            _render_trace(reply)


def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
