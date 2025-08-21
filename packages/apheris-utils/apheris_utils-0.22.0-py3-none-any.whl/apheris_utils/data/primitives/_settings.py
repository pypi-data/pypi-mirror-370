import os
from pathlib import Path
from typing import Dict, Union

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file() -> Union[Path, str, None]:
    """Supports multiple environment configurations based on the
    APH_ENV environment variable.

    The default environment will be always local.
    """
    # Make sure we don't load a spurious .env file by mistake
    env_name = os.getenv("APH_ENV", "local")
    env_file_prefix = ".env"
    env_file_path = f"{env_file_prefix}-{env_name.lower()}"

    return env_file_path if os.path.exists(env_file_path) else None


class DALSettings(BaseSettings):
    api_dal_url: AnyHttpUrl = AnyHttpUrl("http://test-api")
    dal_token: str = "test-token"
    data: Dict[str, str] = Field(default_factory=lambda: {"test": "test-dataset"})
    max_workers: int = 50
    timeout: int = 600

    is_local_simulator: bool = False

    model_config = SettingsConfigDict(
        env_prefix="APH_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.dal_token}"}

    @property
    def dataset_endpoint(self) -> str:
        # HttpUrl type adds a trailing slash
        return f"{self.api_dal_url}datasets/"

    @property
    def policy_endpoint(self) -> str:
        return f"{self.api_dal_url}policies/"

    @property
    def persist_endpoint(self) -> str:
        return f"{self.api_dal_url}dataset/"


def get_settings():
    return DALSettings(_env_file=get_env_file())
