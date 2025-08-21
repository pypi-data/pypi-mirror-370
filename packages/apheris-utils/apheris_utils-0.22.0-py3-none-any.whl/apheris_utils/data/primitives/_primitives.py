from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..._session import create_session_with_retries
from ._settings import get_settings


class RemoteFile(BaseModel):
    """
    RemoteFile encapsulates the details about the data including its internal key and the path used for local processing.

    Attributes:
        _key (str): The internal key to access the data, typically a URL like s3://data/object.csv.
        _parent (str): The parent key if the file is part of a dataset with a folder key. Example: parent = s3://data/
        path (str): The path derived from the _key for local processing or storage. This is calculated based on prefix provided during initialization.
    """

    id: str
    key: str = Field(..., alias="_key")
    parent: Optional[str] = Field(None, alias="_parent")

    @property
    def path(self) -> str:
        core_path: str
        if self.parent:
            # With key s3://folder/data/data.csv and parent s3://folder/ the core path is data/data.csv
            core_path = self.key[len(self.parent) :]
        else:  # with key file:///data.csv the core path is data.csv
            core_path = self.key.split("/")[-1:][0]

        return f"{self.id}/{core_path}"


def list_remote_files(dataset_id: str) -> List[RemoteFile]:
    """
    Retrieves a list of remote files corresponding to all files contained within a specified dataset identified by its unique dataset id.
    The unique dataset can be seen by listing datasets
    A dataset ID is a unique identifier that can be used to access specific datasets in a data access layer (DAL).
    Returns:
        List[str]: A list of keys representing remote files that are accessible through the DAL.
    """
    settings = get_settings()
    key = settings.data[dataset_id]

    _session = create_session_with_retries()

    if key.endswith("/"):
        if settings.is_local_simulator:
            raise NotImplementedError(
                "Multi-file datasets are not currently supported in the local simulator."
            )

        r = _session.get(f"{settings.dataset_endpoint}{key}", headers=settings.headers)

        if r.status_code != 200:
            raise RuntimeError(f"Failed to list datasets: {r.text}")

        keys = r.json()
        while link := r.headers.get("Link"):
            r = _session.get(
                f"{settings.dataset_endpoint}{link}", headers=settings.headers
            )
            keys += r.json()

        files = [RemoteFile(id=dataset_id, _key=k, _parent=key) for k in keys]
    else:
        files = [RemoteFile(id=dataset_id, _key=key, _parent=None)]

    return files


def get(
    remote_files: Union[RemoteFile, List[RemoteFile]],
    output_func: Callable[[RemoteFile, bytes], Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Fetches the data specified by `remote_files` and applies a provided output function to handle the retrieved content.

    Args:
        remote_files (Union[RemoteFile, List[RemoteFile]]): A single RemoteFile or a list of RemoteFiles to retrieve.
        output_func (Callable[[RemoteFile, bytes], Dict[str,Any]]): A function that processes the retrieved data. It accepts
                                                                   the RemoteFile object and its content in bytes.

    Returns:
        Dict[str, Any]: A dictionary mapping keys to the processed results from the output function.
                       For single files, returns the direct output dictionary.
                       For multiple files, returns a merged dictionary of all results.
    """
    settings = get_settings()
    _session = create_session_with_retries()

    if isinstance(remote_files, RemoteFile):
        r = _session.get(
            f"{settings.dataset_endpoint}{remote_files.key}", headers=settings.headers
        )
        if r.status_code != 200:
            raise RuntimeError(f"Failed to get key: {r.text}")

        # If using the dummy DAL simulator, it returns an empty content for the file
        # if no dummy data has been registered for that dataset. Raise an error to help
        # with debugging.
        if settings.is_local_simulator and not r.content:
            raise RuntimeError(
                f"Dummy data for {remote_files.key} is empty, please check with the Data Custodian"
                "to ensure that a dummy dataset has been registered."
            )

        return output_func(remote_files, r.content)

    with ThreadPoolExecutor(max_workers=get_settings().max_workers) as executor:
        results = executor.map(partial(get, output_func=output_func), remote_files)
        return {k: v for result in results for k, v in result.items()}


def to_folder(folder: Union[str, Path]) -> Callable[[RemoteFile, bytes], Dict[str, Path]]:
    """
    Create a callable function for saving content to a specified folder.

    Args:
        folder (Union[str, Path]): The root directory where files will be saved.

    Returns:
        Callable[[RemoteFile, bytes], Dict[str, Any]]: A function that takes a RemoteFile and its content as bytes,
                                                      then saves it to the destination derived from the RemoteFile's path
                                                      and returns a dict mapping the RemoteFile's ID to the saved path.
    """
    if isinstance(folder, str):
        folder = Path(folder)

    folder = folder.resolve()  # Ensure the folder path is absolute and resolved

    # Make sure folder exists
    folder.mkdir(parents=True, exist_ok=True)

    def output_func(remote_file: RemoteFile, content: bytes) -> Dict[str, Path]:
        # Parse key to extract the complete path excluding the protocol
        # Example paths:
        # s3://data/folder1/folder2/data.csv -> folder1/folder2/data.csv
        # file:///container/folder1/folder2 -> container/folder1/folder2
        full_path = folder / remote_file.path

        if not full_path.resolve().is_relative_to(folder):
            raise ValueError("Access denied: Path traversal attempt detected")

        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(content)

        # If it's a container dataset, return the destination folder e.g. destination/slug/
        if remote_file.parent:
            return {remote_file.id: folder / remote_file.id}

        # If not return the full path e.g. destination/slug/data.csv
        return {remote_file.id: full_path}

    return output_func


def to_dict() -> Callable[[RemoteFile, bytes], Dict[str, Any]]:
    """
    Create a callable that stores content bytes in a dictionary under RemoteFile's ID.

    Returns:
        Callable[[RemoteFile, bytes], Dict[str, Any]]: A function that takes a RemoteFile and content bytes,
        returning a dictionary mapping the RemoteFile's ID to its content.
    """

    def output_func(remote_file: RemoteFile, content: bytes):
        return {remote_file.path: content}

    return output_func
