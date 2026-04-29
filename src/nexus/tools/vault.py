from pathlib import Path

from nexus.config import VAULT_PATH


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
        full_path = _safe_path(f"{path}.md")
        return full_path.read_text(encoding="utf-8")
    except ValueError as exc:
        return f"Erro: {exc}"
    except FileNotFoundError:
        return f"Erro: Documento '{path}.md' não encontrado no vault."
    except PermissionError:
        return f"Erro: Sem permissão para ler '{path}.md'."
    except OSError as exc:
        return f"Erro de I/O ao ler '{path}': {exc}"


def update_memory(content: str) -> str:
    """
    Adiciona uma nova linha à memória do agente no arquivo memoria/historico.md.
    Use sempre que o usuário pedir para anotar, lembrar ou registrar algo importante.
    O conteúdo é adicionado como um bullet point Markdown.
    """
    try:
        history_path = VAULT_PATH / "memoria" / "historico.md"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with history_path.open("a", encoding="utf-8") as f:
            f.write(f"\n- {content}")
        return "Memória atualizada com sucesso."
    except PermissionError:
        return f"Erro ao escrever memória: sem permissão para acessar o arquivo."
    except OSError as exc:
        return f"Erro ao escrever memória: {exc}"
