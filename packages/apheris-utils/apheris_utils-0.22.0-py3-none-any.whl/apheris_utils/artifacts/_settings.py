from typing import Dict

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class ArtifactsSettings(BaseSettings):
    """Configuration settings for the artifacts module.

    This class manages all configuration settings required for artifact operations,
    including API endpoints and authentication tokens. Settings can be overridden
    via environment variables with the 'APH_' prefix.

    Attributes:
        api_orchestrator_base_url: Base URL for the orchestrator API service
        auth_data_artifact_token: Authentication token for artifact operations

    Environment Variables:
        APH_API_ORCHESTRATOR_BASE_URL: Override the base URL
        APH_AUTH_DATA_ARTIFACT_TOKEN: Override the authentication token
    """

    api_orchestrator_base_url: AnyHttpUrl = AnyHttpUrl("http://orchestrator")
    auth_data_artifact_token: str = "test-token"

    model_config = SettingsConfigDict(env_prefix="APH_", env_file_encoding="utf-8")

    @property
    def headers(self) -> Dict[str, str]:
        """Generate HTTP headers for API requests.

        Returns:
            Dict[str, str]: Headers dictionary with authorization bearer token
        """
        return {"Authorization": f"Bearer {self.auth_data_artifact_token}"}

    @property
    def artifacts_endpoint(self) -> str:
        """Get the complete artifacts API endpoint URL.

        Returns:
            str: Full URL path to the artifacts API endpoint
        """
        return f"{self.api_orchestrator_base_url}v1/artifacts/"


def get_settings() -> ArtifactsSettings:
    """Get the current artifacts settings instance.

    Returns:
        ArtifactsSettings: Configured settings instance with environment overrides applied
    """
    return ArtifactsSettings()
