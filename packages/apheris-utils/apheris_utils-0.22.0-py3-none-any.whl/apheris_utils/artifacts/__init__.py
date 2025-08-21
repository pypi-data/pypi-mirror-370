"""Apheris Artifacts Module.

This module provides functionality for managing machine learning artifacts including
models, datasets, checkpoints, and logs. It supports creating, uploading, downloading,
and managing files associated with ML workflows.

The main classes are:
- Artifact: Represents an ML artifact with metadata and associated files
- ArtifactType: Enum defining the types of artifacts (MODEL, DATASET, etc.)

Example:
    Creating and uploading an artifact with files:

    >>> from apheris_utils.artifacts import Artifact, ArtifactType
    >>> from uuid import uuid4
    >>>
    >>> artifact = Artifact(
    ...     job_id=uuid4(),
    ...     type=ArtifactType.MODEL,
    ...     name="my-model",
    ...     metadata={"version": "1.0", "accuracy": 0.95}
    ... )
    >>> artifact.add_file(local_path="model.pkl")
    >>> artifact.save()
"""

from ._artifacts import (
    Artifact,
    ArtifactType,
    create_artifact_from_bytes,
    create_artifact_from_file,
)

__all__ = [
    "Artifact",
    "ArtifactType",
    "create_artifact_from_file",
    "create_artifact_from_bytes",
]
