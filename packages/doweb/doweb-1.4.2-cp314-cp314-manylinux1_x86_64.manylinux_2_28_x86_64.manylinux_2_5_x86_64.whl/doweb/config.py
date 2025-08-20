from __future__ import annotations

from pathlib import Path

import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="doweb_", env_nested_delimiter="_")
    fileslocation: Path
    meta_splitter: str = ":"
    editable: bool = False
    add_missing_layers: bool = True
    max_rdb_limit: int = 1000
    """Maximum rdb errors the client can request."""

    @pydantic.field_validator("fileslocation")
    @classmethod
    def resolvefileslocation(cls, v: Path | str) -> Path:
        return Path(v).expanduser().resolve()
