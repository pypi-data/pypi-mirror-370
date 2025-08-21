import json
import os

from apheris_auth.config import settings as auth_settings
from apheris_auth.core.auth import get_session
from apheris_auth.core.exceptions import Unauthorized


def _get_oauth_token() -> str:
    try:
        session, _ = get_session()
        return session.token["access_token"]
    except Unauthorized:
        raise RuntimeError("You are not logged in. Please log in using the Apheris CLI.")


def _get_download_endpoint() -> str:
    orch_url = auth_settings.API_ORCHESTRATOR_BASE_URL
    orch_url = orch_url.rstrip("/")  # Ensure no trailing slash
    return f"{orch_url}/dev/dal/"


def configure_env(dataset_ids: list[str] | None = None) -> None:
    """
    Configure the environment for the Apheris Data Access Layer (DAL) simulator.
    This function sets the necessary environment variables to simulate the DAL
    behavior in a local environment.

    Args:
        dataset_ids (list[str] | None): A list of dataset IDs to simulate. If None,
            it will use the dataset IDs from the environment variable APH_DATA.
            Defaults to None.
    """

    os.environ["APH_API_DAL_URL"] = _get_download_endpoint()
    os.environ["APH_DAL_TOKEN"] = _get_oauth_token()

    # Order of preference for dataset_ids:
    # 1. Provided dataset_ids argument
    # 2. Environment variable APH_DATA
    # 3. Default empty dictionary if APH_DATA is not set
    if dataset_ids:
        # The real DAL provides a mapping of dataset IDs to their actual file paths.
        # The dummy DAL uses the dataset ID as both the key and the value.
        data_dict = {dataset_id: dataset_id for dataset_id in dataset_ids}
    else:
        data_dict = json.loads(os.getenv("APH_DATA", "{}"))

    os.environ["APH_DATA"] = json.dumps(data_dict)

    os.environ["APH_IS_LOCAL_SIMULATOR"] = "1"
