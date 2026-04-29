from pathlib import Path

from pydantic import BaseModel, field_validator, ValidationError

from nexus.config import VAULT_PATH


class VaultReadArgs(BaseModel):
    path: str

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        v = v.strip().lstrip("/")
        if not v:
            raise ValueError("O caminho não pode ser vazio.")
        if ".." in v.split("/"):
            raise ValueError("Path traversal ('..') não é permitido.")
        return v


class MemoryWriteArgs(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("O conteúdo da memória não pode ser vazio.")
        if len(v) > 2000:
            raise ValueError("Conteúdo excede 2000 caracteres.")
        return v


def _safe_path(relative: str) -> Path:
    target = (VAULT_PATH / relative).resolve()
    if not target.is_relative_to(VAULT_PATH):
        raise ValueError(
            f"Acesso negado: o caminho '{relative}' está fora do vault permitido."
        )
    return target


def read_vault(path: str) -> str:
    """
    Lê arquivos do vault do Obsidian.
    Uso sugerido: 'docs/perfil' para identidade, 'memoria/historico' para histórico.
    Retorna o conteúdo do arquivo como texto ou uma mensagem de erro clara.
    """
    try:
        args = VaultReadArgs(path=path)
    except ValidationError as exc:
        first_error = exc.errors()[0]["msg"]
        return f"Erro: argumento inválido — {first_error}"
    try:
        full_path = _safe_path(f"{args.path}.md")
        return full_path.read_text(encoding="utf-8")
    except ValueError as exc:
        return f"Erro: {exc}"
    except FileNotFoundError:
        return f"Erro: Documento '{args.path}.md' não encontrado no vault."
    except PermissionError:
        return f"Erro: Sem permissão para ler '{args.path}.md'."
    except OSError as exc:
        return f"Erro de I/O ao ler '{args.path}': {exc}"


def update_memory(content: str) -> str:
    """
    Adiciona uma nova linha à memória do agente no arquivo memoria/historico.md.
    Use sempre que o usuário pedir para anotar, lembrar ou registrar algo importante.
    O conteúdo é adicionado como um bullet point Markdown.
    """
    try:
        args = MemoryWriteArgs(content=content)
    except ValidationError as exc:
        first_error = exc.errors()[0]["msg"]
        return f"Erro: argumento inválido — {first_error}"
    try:
        history_path = VAULT_PATH / "memoria" / "historico.md"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with history_path.open("a", encoding="utf-8") as f:
            f.write(f"\n- {args.content}")
        return "Memória atualizada com sucesso."
    except PermissionError:
        return "Erro ao escrever memória: sem permissão para acessar o arquivo."
    except OSError as exc:
        return f"Erro ao escrever memória: {exc}"
