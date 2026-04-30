from agentscope.tool import Toolkit

from nexus.settings import NexusSettings
from nexus.tools.vault import make_read_vault, make_update_memory


def register_default_tools(toolkit: Toolkit, settings: NexusSettings) -> None:
    """Registra todas as ferramentas padrão do Nexus no toolkit fornecido."""
    toolkit.register_tool_function(
        make_read_vault(settings), func_name="read_vault"
    )
    toolkit.register_tool_function(
        make_update_memory(settings), func_name="update_memory"
    )
