from pydantic import BaseModel, Field, field_validator


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


class NexusReply(BaseModel):
    """Resposta estruturada do Nexus, validada a cada turno do agente."""

    answer: str = Field(
        description=(
            "Resposta final ao usuário, em português, em prosa natural. "
            "Sem JSON, sem chamadas de função, sem blocos de código."
        ),
    )
    sources_consulted: list[str] = Field(
        default_factory=list,
        description=(
            "Lista dos caminhos do Vault que foram lidos via read_vault neste turno "
            "(ex.: ['docs/perfil']). Lista vazia se nenhum arquivo foi consultado."
        ),
    )
    wrote_memory: bool = Field(
        default=False,
        description=(
            "True se update_memory foi chamado com sucesso neste turno. "
            "False caso contrário."
        ),
    )


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
