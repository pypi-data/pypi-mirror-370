from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

from .._session import create_session_with_retries
from .primitives import get, get_settings, list_remote_files, to_folder


def get_asset_policies(
    dataset_ids: Union[str, List[str]],
) -> Dict[str, Dict[str, Any]]:
    """
    Retrieves policy details for one or more datasets from the configured policy endpoint.

    Args:
        dataset_ids (Union[str, List[str]]): A single dataset id or a list of dataset ids for which policies are requested.

    Raises:
        RuntimeError: If the request to the policy endpoint fails.

    Returns:
        Union[Dict[str, Any], Dict[str, Dict[str, Any]]]: A dictionary containing the policy details for the requested dataset(s).
        If called with a single dataset id, returns a dictionary with the policy details. If called with a list of dataset ids,
        returns a dictionary of dictionaries with each dataset's policy details.
    """
    settings = get_settings()
    if settings.is_local_simulator:
        raise NotImplementedError(
            "Asset policies are not implemented in the local simulator."
        )

    _session = create_session_with_retries()
    if isinstance(dataset_ids, str):
        r = _session.get(
            f"{settings.policy_endpoint}{settings.data[dataset_ids]}",
            headers=settings.headers,
        )
        if r.status_code != 200:
            raise RuntimeError(f"Failed to get policy: {r.text}")

        return {dataset_ids: r.json()}

    policies = {}
    for d in dataset_ids:
        policies.update(get_asset_policies(d))

    return policies


# Alias to load_dataset
def download_dataset(dataset_id: str, folder: Union[str, Path]) -> Dict[str, Path]:
    """
    Load a dataset from the DAL and save it to a folder.

    Args:
        dataset_id (str): The ID of the dataset to load.
        folder (Union[str, Path]): The folder where the dataset will be saved.

    Returns:
        Dict[str,str]: A dictionary mapping dataset id to their saved locations
    """
    return get(list_remote_files(dataset_id), to_folder(folder))


def list_dataset_ids() -> List[str]:
    """
    List all available dataset ids.

    Returns:
        List[str]: A list of all available dataset ids.
    """
    settings = get_settings()
    return list(settings.data.keys())


# Alias to download all datasets
def download_all(folder: Union[str, Path]) -> Dict[str, Path]:
    """
    Downloads all datasets specified in the settings and saves them to the provided folder.

    Args:
        folder (Union[str, Path]): The path to the directory where the datasets will be stored.

    Returns:
        Dict[str, Union[str, Dict[str,str]]]: A dictionary mapping dataset IDs to their saved locations
    """
    # We get a list of dataset ids such as `my-data`, `my-slug`
    dataset_ids = list_dataset_ids()
    output = {}
    for dataset_id in dataset_ids:
        remote_files = list_remote_files(dataset_id)
        output.update(get(remote_files, to_folder(folder)))
    return output


def persist_bytes(dataset_name: str, contents: bytes, file_name: str):
    """
    Persist a file via the Apheris Data Access Layer (DAL) using the dataset name as a
    prefix.

    Datasets are scoped to a user, so the dataset name should be unique to the user.
    Note that the dataset name is not scoped to the originating model, so it is
    recommended to use a unique dataset name for each model or experiment.

    Args:
        dataset_name: The name of the dataset to which the file will be persisted.
        contents: The contents of the file to be persisted, as bytes.
        file_name: The name of the file to be persisted.
    """
    settings = get_settings()

    url = f"{settings.persist_endpoint}{dataset_name}/{file_name}"

    r = requests.put(
        url, data=contents, headers=settings.headers, timeout=settings.timeout
    )
    r.raise_for_status()


def persist_file(
    dataset_name: str, file_to_persist: Path, file_name: Optional[str] = None
):
    """
    Persist a file via the Apheris Data Access Layer (DAL) using the dataset name as a
    prefix.

    Datasets are scoped to a user, so the dataset name should be unique to the user.
    Note that the dataset name is not scoped to the originating model, so it is
    recommended to use a unique dataset name for each model or experiment.

    Args:
        dataset_name: The name of the dataset to which the file will be persisted.
        file_to_persist: The path to the file to be persisted.
        file_name: Optional; the name under which the file will be stored in the dataset.
                   If not provided, the original file name will be used.
    """

    with open(file_to_persist, "rb") as f:
        contents = f.read()

    persist_bytes(dataset_name, contents, file_name or file_to_persist.name)
