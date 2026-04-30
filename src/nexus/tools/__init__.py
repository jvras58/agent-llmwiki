from pathlib import Path

from agentscope.tool import Toolkit

from nexus.tools.vault import make_read_vault, make_update_memory


def register_default_tools(toolkit: Toolkit, vault_root: Path) -> None:
    """Registra todas as ferramentas padrão do Nexus no toolkit fornecido."""
    toolkit.register_tool_function(
        make_read_vault(vault_root), func_name="read_vault"
    )
    toolkit.register_tool_function(
        make_update_memory(vault_root), func_name="update_memory"
    )


__all__ = ["register_default_tools"]
