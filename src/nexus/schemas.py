from pydantic import BaseModel, field_validator


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
