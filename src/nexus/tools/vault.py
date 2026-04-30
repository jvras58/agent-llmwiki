import logging
from pathlib import Path

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse
from pydantic import ValidationError

from nexus.schemas import MemoryWriteArgs, VaultReadArgs
from nexus.services.vault import (
    VaultPathError,
    append_memory,
    read_document,
)
from nexus.tools._normalize import extract_str

logger = logging.getLogger(__name__)


def _text_response(text: str) -> ToolResponse:
    return ToolResponse(content=[TextBlock(type="text", text=text)])


def _validation_error_message(exc: ValidationError) -> str:
    first_error = exc.errors()[0]["msg"]
    return f"Erro: argumento inválido — {first_error}"


def make_read_vault(vault_root: Path):
    def read_vault(path: str) -> ToolResponse:
        """
        Lê arquivos do vault do Obsidian.
        Uso sugerido: 'docs/perfil' para identidade, 'memoria/historico' para histórico.
        Retorna o conteúdo do arquivo como texto ou uma mensagem de erro clara.
        """
        try:
            args = VaultReadArgs(path=extract_str(path))
        except ValidationError as exc:
            return _text_response(_validation_error_message(exc))

        try:
            content = read_document(vault_root, args.path)
        except VaultPathError as exc:
            return _text_response(f"Erro: {exc}")
        except FileNotFoundError:
            return _text_response(
                f"Erro: Documento '{args.path}.md' não encontrado no vault."
            )
        except PermissionError:
            return _text_response(f"Erro: Sem permissão para ler '{args.path}.md'.")
        except OSError as exc:
            logger.exception("Falha de I/O lendo %s", args.path)
            return _text_response(f"Erro de I/O ao ler '{args.path}': {exc}")

        return _text_response(content)

    return read_vault


def make_update_memory(vault_root: Path):
    def update_memory(content: str) -> ToolResponse:
        """
        Adiciona uma nova linha à memória do agente no arquivo memoria/historico.md.
        Use sempre que o usuário pedir para anotar, lembrar ou registrar algo importante.
        O conteúdo é adicionado como um bullet point Markdown.
        """
        try:
            args = MemoryWriteArgs(content=extract_str(content))
        except ValidationError as exc:
            return _text_response(_validation_error_message(exc))

        try:
            append_memory(vault_root, args.content)
        except PermissionError:
            return _text_response(
                "Erro ao escrever memória: sem permissão para acessar o arquivo."
            )
        except OSError as exc:
            logger.exception("Falha de I/O ao gravar memória")
            return _text_response(f"Erro ao escrever memória: {exc}")

        return _text_response("Memória atualizada com sucesso.")

    return update_memory
