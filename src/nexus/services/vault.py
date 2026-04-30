from pathlib import Path


class VaultPathError(ValueError):
    """Caminho fora do sandbox do Vault."""


def _safe_path(vault_root: Path, relative: str) -> Path:
    target = (vault_root / relative).resolve()
    if not target.is_relative_to(vault_root):
        raise VaultPathError(
            f"Acesso negado: o caminho '{relative}' está fora do vault permitido."
        )
    return target


def read_document(vault_root: Path, relative_path: str) -> str:
    """Lê um documento Markdown do Vault.

    Levanta:
        VaultPathError: caminho fora do sandbox.
        FileNotFoundError: arquivo inexistente.
        PermissionError: sem permissão de leitura.
        OSError: outros erros de I/O.
    """
    full_path = _safe_path(vault_root, f"{relative_path}.md")
    return full_path.read_text(encoding="utf-8")


def append_memory(vault_root: Path, content: str) -> None:
    """Adiciona uma linha à memória append-only em memoria/historico.md.

    Levanta:
        PermissionError: sem permissão de escrita.
        OSError: outros erros de I/O.
    """
    history_path = vault_root / "memoria" / "historico.md"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as f:
        f.write(f"\n- {content}")
