from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import requests
from pydantic import BaseModel, ConfigDict, Field

from .._session import create_session_with_retries
from ._files import NewArtifactFile, SavedArtifactFile
from ._settings import get_settings
from ._utils import convert_uuid_fields


class ArtifactType(str, Enum):
    """Enum defining the available artifact types.

    This enum represents the different types of artifacts that can be created
    and managed within the system.

    Attributes:
        CHECKPOINT: Model training checkpoint files
        METRIC: Metric files for trained machine learning models
        RESULT: Result files from model training or inference
        LOG: Log files from training or inference
    """

    CHECKPOINT = "checkpoint"
    METRIC = "metric"
    RESULT = "result"
    LOG = "log"


class CreatedBy(BaseModel):
    """Information about the user who created an artifact.

    This model contains metadata about the user responsible for creating
    an artifact, providing traceability and audit information.

    Attributes:
        user: The username or identifier of the user who created the artifact
    """

    user: str


class Artifact(BaseModel):
    """A machine learning artifact containing files and metadata.

    This class represents an artifact in the system, which can contain multiple files
    along with associated metadata. Artifacts are used to store and manage various
    types of ML assets like models, datasets, checkpoints, and logs.

    Attributes:
        id: Unique identifier for the artifact (auto-generated when saved)
        job_id: ID of the job that created this artifact
        type: The type of artifact (model, dataset, checkpoint, or log)
        name: Human-readable name for the artifact
        metadata: Additional metadata as string or dictionary
        created_by: Information about who created the artifact
        files: List of files associated with this artifact
    """

    id: Optional[UUID] = Field(default=None, alias="ID")
    job_id: UUID = Field(alias="jobID")
    type: ArtifactType
    name: str
    metadata: str | Dict[str, Any] = Field(default_factory=lambda: {})
    created_by: Optional[CreatedBy] = Field(None, alias="createdBy")

    files: List[SavedArtifactFile] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def model_post_init(self, __context: Any) -> None:
        """Initialize additional attributes after Pydantic model initialization."""
        self._new_files: List[NewArtifactFile] = []

    def add_file(
        self,
        local_path: Optional[Path | str] = None,
        data: Optional[bytes] = None,
        filename: Optional[str] = None,
    ) -> None:
        """Add a file to the artifact for later upload.

        This method prepares a file for upload by creating a NewArtifactFile object
        and adding it to the internal list. The actual upload occurs when save() is called.

        Args:
            local_path: Path to a local file to upload
            data: Raw bytes data to upload (alternative to local_path)
            filename: Name for the file when using raw data

        Raises:
            ValueError: If neither local_path nor data is provided, or if both are provided
            FileNotFoundError: If local_path is specified but the file doesn't exist
        """
        if isinstance(local_path, str):
            local_path = Path(local_path).resolve()
        file = NewArtifactFile(local_path=local_path, data=data, filename=filename)
        self._new_files.append(file)

    def _create_artifact(self) -> UUID:
        """Create the artifact on the server and return its ID.

        This private method handles the HTTP request to create a new artifact
        on the server. It serializes the artifact data and sends it via POST.

        Returns:
            UUID: The unique identifier assigned to the created artifact

        Raises:
            ValueError: If the server returns an error response
        """
        settings = get_settings()

        artifact_dict = self.model_dump(
            by_alias=True, exclude={"files", "_new_files", "id"}
        )

        headers = settings.headers.copy()
        headers["Content-Type"] = "application/json"

        try:
            response = create_session_with_retries().post(
                settings.artifacts_endpoint,
                headers=headers,
                json=convert_uuid_fields(artifact_dict),
            )

            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ValueError(f"Failed to create artifact: {response.text}")

        return UUID(response.json()["id"])

    def save(self) -> None:
        """Save the artifact and upload all associated files.

        This method creates the artifact on the server (if not already created)
        and uploads all files that have been added via add_file(). The upload
        process is atomic - if any file upload fails, the entire operation fails.

        Raises:
            ValueError: If artifact creation fails
            RuntimeError: If any file upload fails
        """
        if not self.id:
            self.id = self._create_artifact()

        for file in self._new_files:
            file.upload(self.id, self.job_id)

    @staticmethod
    def get(artifact_id: UUID | str) -> "Artifact":
        """Fetch an artifact by its ID from the server.

        Args:
            artifact_id: The unique identifier of the artifact to fetch.
                        Can be provided as UUID or string.

        Returns:
            Artifact: The fetched artifact object with all its metadata and files.

        Raises:
            requests.exceptions.HTTPError: If the server returns an error response
            ValueError: If the artifact_id is invalid
        """

        if isinstance(artifact_id, str):
            artifact_id = UUID(artifact_id)

        settings = get_settings()

        response = create_session_with_retries().get(
            f"{settings.artifacts_endpoint}{artifact_id}",
            headers=settings.headers,
        )

        response.raise_for_status()

        return Artifact.model_validate(response.json())


def _create_artifact(
    job_id: UUID,
    artifact_type: ArtifactType,
    name: str,
    file_path: Path | None = None,
    data: bytes | None = None,
    file_name: str | None = None,
    metadata: Dict[str, Any] | None = None,
    created_by: CreatedBy | str | None = None,
) -> Artifact:
    """Create a new artifact with the specified files and metadata.

    Args:
        file_paths: List of file paths to include in the artifact
        job_id: ID of the job that created this artifact
        artifact_type: Type of the artifact (e.g., CHECKPOINT, METRIC)
        name: Human-readable name for the artifact
        metadata: Additional metadata for the artifact

    Returns:
        Artifact: The created artifact object with all files and metadata
    """
    if metadata is None:
        metadata = {}

    if created_by is None:
        created_by = CreatedBy(user="computation")
    elif isinstance(created_by, str):
        created_by = CreatedBy(user=created_by)

    if file_path is not None and data is not None:
        raise ValueError(
            "Cannot specify both file_path and data to create_artifact. "
            "Please use the Artifact.add_file() method to add files after "
            "creation."
        )
    elif file_path is None and data is None:
        raise ValueError(
            "Must specify either file_path or data to create_artifact. "
            "Please use the Artifact.add_file() method to add files after "
            "creation."
        )

    if file_name is None:
        file_name = file_path.name if file_path else None

    artifact = Artifact(
        job_id=job_id,
        type=artifact_type,
        name=name,
        metadata=metadata,
        createdBy=created_by,
    )

    artifact.add_file(local_path=file_path, data=data, filename=file_name)

    artifact.save()
    return artifact


def create_artifact_from_file(
    job_id: UUID,
    artifact_type: ArtifactType,
    name: str,
    file_path: Path,
    metadata: Dict[str, Any] | None = None,
    created_by: CreatedBy | str | None = None,
) -> Artifact:
    """Create an artifact with a single file or raw data.

    Args:
        job_id: ID of the job that created this artifact
        artifact_type: Type of the artifact (e.g., CHECKPOINT, METRIC)
        name: Human-readable name for the artifact
        file_path: Path to a local file to include in the artifact
        metadata: Additional metadata for the artifact
        created_by: Information about who created the artifact

    Returns:
        Artifact: The created artifact object with all files and metadata
    """
    return _create_artifact(
        job_id=job_id,
        artifact_type=artifact_type,
        name=name,
        file_path=file_path,
        metadata=metadata,
        created_by=created_by,
    )


def create_artifact_from_bytes(
    job_id: UUID,
    artifact_type: ArtifactType,
    name: str,
    data: bytes,
    file_name: str,
    metadata: Dict[str, Any] | None = None,
    created_by: CreatedBy | str | None = None,
) -> Artifact:
    """Create an artifact with a single file or raw data.

    Args:
        job_id: ID of the job that created this artifact
        artifact_type: Type of the artifact (e.g., CHECKPOINT, METRIC)
        name: Human-readable name for the artifact
        data: Raw data to include in the artifact
        file_name: Name for the file when using raw data
        metadata: Additional metadata for the artifact
        created_by: Information about who created the artifact

    Returns:
        Artifact: The created artifact object with all files and metadata
    """
    return _create_artifact(
        job_id=job_id,
        artifact_type=artifact_type,
        name=name,
        data=data,
        file_name=file_name,
        metadata=metadata,
        created_by=created_by,
    )


__all__ = [
    "Artifact",
    "ArtifactType",
    "CreatedBy",
    "create_artifact_from_file",
    "create_artifact_from_bytes",
]
