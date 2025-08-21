from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

import requests
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .._session import create_session_with_retries
from ._settings import get_settings
from ._utils import convert_uuid_fields


class CreateFileRequest(BaseModel):
    """Request model for obtaining a pre-signed URL for file upload.

    This model represents a request to the server to get a self-signed URL
    for uploading a file to an artifact. It includes the job ID and an optional
    payload checksum for integrity verification.

    Attributes:
        job_id: The unique identifier of the job associated with the file
        payload_checksum: Optional MD5 checksum of the file for integrity verification
    """

    job_id: UUID = Field(..., alias="jobID")
    payload_checksum: Optional[str] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class CreateFileResponseHeader(BaseModel):
    """Headers required for uploading files to pre-signed URLs.

    This model represents the headers returned by the server when creating a file.
    These headers must be included in the actual upload request to the pre-signed URL
    to ensure proper authentication and metadata handling.

    Attributes:
        content_md5: MD5 hash header for content verification
        host: Target host header for the upload request
        x_amz_meta_computespec_id: AWS metadata header for compute specification ID
        x_amz_meta_job_id: AWS metadata header for job ID
    """

    content_md5: List[str] | None = Field(default=None, alias="Content-Md5")
    host: List[str] = Field(..., alias="Host")
    x_amz_meta_computespec_id: List[str] = Field(..., alias="X-Amz-Meta-Computespec_id")
    x_amz_meta_job_id: List[str] = Field(..., alias="X-Amz-Meta-Job_id")
    x_amz_meta_server_side_encryption: List[str] = Field(
        ..., alias="X-Amz-Server-Side-Encryption"
    )
    x_amz_meta_server_side_encryption_kms_key_id: List[str] = Field(
        ..., alias="X-Amz-Server-Side-Encryption-Aws-Kms-Key-Id"
    )

    model_config = ConfigDict(extra="forbid")

    def to_headers(self) -> dict:
        """Convert the model to a dictionary suitable for use as HTTP headers.

        Returns:
            dict: A dictionary mapping header names to their values,
                 suitable for use in HTTP requests.
        """
        headers = {
            "Host": self.host[0],
            "X-Amz-Meta-Computespec_id": self.x_amz_meta_computespec_id[0],
            "X-Amz-Meta-Job_id": self.x_amz_meta_job_id[0],
            "X-Amz-Server-Side-Encryption": self.x_amz_meta_server_side_encryption[0],
            "X-Amz-Server-Side-Encryption-Aws-Kms-Key-Id": self.x_amz_meta_server_side_encryption_kms_key_id[
                0
            ],
        }
        if self.content_md5:
            headers["Content-Md5"] = self.content_md5[0]
        return headers


class CreateFileResponse(BaseModel):
    """Response containing pre-signed URL and headers for file upload.

    When creating a file, the server responds with a pre-signed URL and headers
    that can be used to upload the file directly to the storage service.
    This bypasses the API server for file uploads, enabling direct storage access.

    Attributes:
        fileId: The unique identifier assigned to the file
        url: The pre-signed URL for direct file upload
        headers: Required headers for the upload request
    """

    fileId: UUID = Field(..., alias="fileID")
    url: str
    headers: CreateFileResponseHeader = Field(..., alias="headers")

    model_config = ConfigDict(extra="forbid")


class FetchFileResponse(BaseModel):
    """Response containing pre-signed URL and checksum for file download.

    This model represents the server response when requesting to download a file.
    It contains the pre-signed URL for secure file download and an optional
    MD5 checksum for integrity verification.

    Attributes:
        url: The pre-signed URL from which to securely download the file
        checksum: Optional MD5 checksum for verifying file integrity after download
    """

    url: str
    checksum: Optional[str] = None


def _hash_bytes(data: bytes) -> str:
    """Calculate the MD5 checksum of the given bytes.

    Args:
        data: The byte data to calculate the checksum for

    Returns:
        str: The MD5 checksum as a hexadecimal string
    """
    import hashlib

    md5_hash = hashlib.md5(data)
    return md5_hash.hexdigest()


def _hash_file(file_path: Path) -> str:
    """Calculate the MD5 checksum of a file.

    Args:
        file_path: The path to the file to calculate the checksum for

    Returns:
        str: The MD5 checksum as a hexadecimal string

    Raises:
        FileNotFoundError: If the specified file does not exist
    """
    import hashlib

    if not file_path.exists():
        raise FileNotFoundError(f"The specified file does not exist: {file_path}")

    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


class SavedArtifactFile(BaseModel):
    """A file that has been saved to an artifact on the server.

    This model represents a file that exists within an artifact and has been
    successfully uploaded to the storage service. It contains metadata about
    the file including its location, hash, and current status.

    Attributes:
        id: Unique identifier for the file
        artifact_id: ID of the artifact this file belongs to
        name: Original filename
        s3_path: Storage path where the file is located
        hash: MD5 hash of the file content
        status: Current status of the file (e.g., 'pending', 'uploaded')
    """

    id: UUID
    artifact_id: UUID = Field(..., alias="artifactID")
    name: str
    s3_path: str = Field(..., alias="s3Path")
    hash: str | None = None
    status: str

    def _get_fetch_url(self) -> Tuple[str, Optional[str]]:
        """Get the pre-signed URL for downloading this file.

        Returns:
            Tuple[str, Optional[str]]: A tuple containing the download URL and
                                     optional checksum for verification

        Raises:
            requests.exceptions.HTTPError: If the server returns an error response
        """
        settings = get_settings()

        url = f"{settings.artifacts_endpoint}{self.artifact_id}/file/{self.name}"

        raw_response = create_session_with_retries().get(
            url,
            headers=settings.headers,
        )

        raw_response.raise_for_status()
        response = FetchFileResponse.model_validate(raw_response.json())
        return response.url, response.checksum

    def fetch(self) -> bytes:
        """Download and return the file content as bytes.

        This method downloads the file from the storage service and verifies
        its integrity using the provided checksum if available.

        Returns:
            bytes: The complete file content

        Raises:
            requests.exceptions.HTTPError: If download fails
            RuntimeError: If checksum verification fails
        """
        url, checksum = self._get_fetch_url()

        response = create_session_with_retries().get(url)
        response.raise_for_status()
        data = response.content
        if checksum and not self._verify_checksum(data, checksum):
            raise RuntimeError(
                "Checksum verification failed. The downloaded file may be corrupted."
            )
        return data

    def _verify_checksum(self, data: bytes, checksum: str) -> bool:
        """Verify the checksum of downloaded data.

        Args:
            data: The downloaded file data
            checksum: The expected checksum to verify against

        Returns:
            bool: True if the checksum matches, False otherwise
        """
        return _hash_bytes(data) == checksum


class NewArtifactFile:
    """A file ready to be uploaded to an artifact.

    This class represents a file that can be uploaded to an artifact. It handles
    both local file paths and raw data uploads, manages checksum calculation,
    and coordinates the multi-step upload process using pre-signed URLs.

    The upload process involves:
    1. Getting a pre-signed URL from the server
    2. Uploading the file data directly to storage
    3. Finalizing the upload by notifying the server

    Attributes:
        file_id: Unique identifier assigned after successful upload initiation

    Args:
        local_path: Path to a local file to be uploaded (mutually exclusive with data)
        data: Raw bytes to be uploaded (mutually exclusive with local_path)
        filename: Name for the uploaded file (required when using data)

    Raises:
        ValueError: If neither local_path nor data is provided, if both are provided,
                   or if filename is not provided when using data
        FileNotFoundError: If the specified local_path does not exist
    """

    _local_path: Optional[Path] = None

    _filename: Optional[str] = None
    _data: Optional[bytes] = None

    file_id: Optional[UUID] = None

    def __init__(
        self,
        local_path: Optional[Path] = None,
        data: Optional[bytes] = None,
        filename: Optional[str] = None,
    ):
        """Initialize the NewArtifactFile with either a local path or raw data.

        Args:
            local_path: Path to a local file to be uploaded
            data: Raw bytes to be uploaded (alternative to local_path)
            filename: Name for the file when using raw data

        Raises:
            ValueError: If validation fails on the provided arguments
            FileNotFoundError: If local_path is specified but doesn't exist
        """
        self._local_path = local_path
        self._data = data

        if local_path is not None:
            local_path = Path(local_path).resolve()

            if data is not None:
                raise ValueError(
                    "Either local_path or data should be provided, not both."
                )

            if not local_path.exists():
                raise FileNotFoundError(
                    f"The specified local path does not exist: {local_path}"
                )
            self._filename = filename if filename else local_path.name
        elif data is not None:
            if filename is None:
                raise ValueError("Filename must be provided if data is provided.")
            self._filename = filename
        else:
            raise ValueError("Either local_path or data must be provided.")

    def _calculate_checksum(self) -> str:
        """Calculate the MD5 checksum of the file or data.

        Returns:
            str: The MD5 checksum as a hexadecimal string

        Raises:
            ValueError: If neither local_path nor data is available
        """

        if self._local_path is not None:
            return _hash_file(self._local_path)
        elif self._data is not None:
            return _hash_bytes(self._data)
        else:
            raise ValueError("Either local_path or data must be provided.")

    def _get_file_path(self, artifact_id: UUID) -> str:
        """Construct the API endpoint path for this file.

        Args:
            artifact_id: The ID of the artifact this file belongs to

        Returns:
            str: The complete API endpoint URL for the file
        """
        settings = get_settings()
        return f"{settings.artifacts_endpoint}{artifact_id}/file/{self._filename}"

    def _get_self_signed_upload_url(
        self,
        artifact_id: UUID,
        job_id: UUID,
        calculate_checksum: bool = True,
    ) -> tuple[str, dict]:
        """Get a pre-signed URL and headers for uploading the file.

        Args:
            artifact_id: The ID of the artifact to upload to
            job_id: The ID of the job creating this file
            calculate_checksum: Whether to calculate and include checksum

        Returns:
            tuple[str, dict]: Pre-signed URL and required headers for upload

        Raises:
            RuntimeError: If the server request fails
        """
        settings = get_settings()
        payload = CreateFileRequest(
            job_id=job_id,
            payload_checksum=(
                self._calculate_checksum()
                if calculate_checksum and self._local_path is not None
                else None
            ),
        )

        payload_dict = convert_uuid_fields(
            payload.model_dump(by_alias=True, exclude_none=True)
        )

        response = create_session_with_retries().put(
            self._get_file_path(artifact_id),
            headers=settings.headers,
            json=payload_dict,
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"Failed to get self-signed upload URL: {response.text}"
            ) from e

        create_file_response = CreateFileResponse.model_validate(response.json())

        self.file_id = create_file_response.fileId

        return create_file_response.url, create_file_response.headers.to_headers()

    def _do_upload(self, self_signed_url: str, headers: dict) -> None:
        """Upload the file data to the pre-signed URL.

        Args:
            self_signed_url: The pre-signed URL to upload to
            headers: Required headers for the upload request

        Raises:
            ValueError: If neither local_path nor data is available
            RuntimeError: If the upload request fails
        """

        if self._local_path is not None:
            with open(self._local_path, "rb") as file:
                data = file.read()
        elif self._data is not None:
            data = self._data
        else:
            raise ValueError("Either local_path or data must be provided.")

        response = create_session_with_retries().request(
            "PUT", self_signed_url, headers=headers, data=data
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Failed to get upload file: {response.text}") from e

    def _finalise_upload(self, artifact_id: UUID, job_id: UUID) -> None:
        """Notify the server that the file upload is complete.

        Args:
            artifact_id: The ID of the artifact the file was uploaded to
            job_id: The ID of the job that created the file

        Raises:
            RuntimeError: If the finalization request fails
        """
        settings = get_settings()

        response = create_session_with_retries().patch(
            f"{settings.artifacts_endpoint}{artifact_id}/file/{self.filename}",
            headers=settings.headers,
            json={"jobID": str(job_id)},
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Failed to finalize upload: {response.text}") from e

    def upload(self, artifact_id: UUID, job_id: UUID) -> None:
        """Upload the file to the artifact using a pre-signed URL.

        This method orchestrates the complete upload process:
        1. Requests a pre-signed URL from the server
        2. Uploads the file data directly to storage
        3. Finalizes the upload by notifying the server

        The upload is atomic - if any step fails, the entire operation fails.

        Args:
            artifact_id: The unique identifier of the target artifact
            job_id: The unique identifier of the job creating this file

        Raises:
            ValueError: If file data is not available
            FileNotFoundError: If local file path doesn't exist
            RuntimeError: If any step of the upload process fails
        """
        url, headers = self._get_self_signed_upload_url(artifact_id, job_id)
        self._do_upload(url, headers)
        self._finalise_upload(artifact_id, job_id)

    @property
    def filename(self) -> str:
        """Get the filename that will be used for the uploaded file.

        Returns:
            str: The filename for the upload (either from local file or specified name)
        """
        return self._filename or ""
