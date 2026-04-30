from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NexusSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEXUS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    vault_path: Path = Field(
        default=Path("./meu_vault"),
        description="Diretório raiz do Vault Obsidian — fonte de verdade do agente.",
    )
    memory_file: Path = Field(
        default=Path("memoria/historico.md"),
        description="Arquivo de memória append-only, relativo ao vault_path.",
    )
    profile_doc: str = Field(
        default="docs/perfil",
        description="Documento de identidade lido em perguntas sobre 'quem é você'.",
    )
    model_name: str = Field(
        default="llama3.2",
        description="Nome do modelo Ollama usado pelo ReActAgent.",
    )
    ollama_host: str | None = Field(
        default=None,
        description="Host do Ollama (ex.: http://localhost:11434). None = default do cliente.",
    )
    max_iters: int = Field(
        default=5,
        ge=1,
        description="Limite de iterações ReAct por turno.",
    )
    log_level: str = Field(
        default="INFO",
        description="Nível de logging (DEBUG, INFO, WARNING, ERROR).",
    )

    @property
    def vault_root(self) -> Path:
        return self.vault_path.expanduser().resolve()


def load_settings() -> NexusSettings:
    return NexusSettings()
