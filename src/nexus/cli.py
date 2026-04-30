import asyncio
import logging

from agentscope.agent import UserAgent
from agentscope.pipeline import MsgHub

from nexus.agents import build_nexus_agent
from nexus.settings import NexusSettings, load_settings

EXIT_SENTINELS = frozenset({"sair", "exit", "quit", "bye"})

logger = logging.getLogger("nexus")


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


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
            await nexus(msg)


def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
