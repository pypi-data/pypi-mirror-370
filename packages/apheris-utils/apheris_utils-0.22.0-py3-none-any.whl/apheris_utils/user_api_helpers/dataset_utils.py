import re
from collections import Counter
from pathlib import Path
from typing import List


def validate_dataset_ids(dataset_ids: List[str]) -> None:
    _validate_type(dataset_ids)
    _validate_each_id_is_unique(dataset_ids)


def _validate_type(dataset_ids: List[str]):
    if not isinstance(dataset_ids, list):
        raise TypeError(
            "The argument `dataset_ids` is not iterable. Please provide a list of "
            "dataset ids."
        )
    if not all([isinstance(id, str) for id in dataset_ids]):
        raise TypeError("Not all elements of `dataset_ids` are strings.")


def _validate_each_id_is_unique(dataset_ids: List[str]) -> None:
    for item, count in Counter(dataset_ids).items():
        if count > 1:
            raise ValueError(
                f"The variable `dataset_ids` contains the value `{item}` {count} times. "
                "This is not supported. Please only list it once."
            )


class LocalDebugDataset:
    """Dataset class for local sessions used in various apheris models, such as
    apheris-statistics and apheris-regression-models. This class is used to create
    a dataset that can be used in local debug sessions."""

    def __init__(
        self,
        dataset_id: str,
        gateway_id: str,
        dataset_fpath: str,
        permissions: dict | None = None,
        policy: dict | None = None,
    ):
        """
        Dataset class for LocalDebugSimpleStatsSessions.

        Args:
            dataset_id: Name of the dataset. Allowed characters: letters, numbers, "_",
                "-", "."
            gateway_id: Name of a hypothetical gateway that this dataset resides on.
                Datasets with the same gateway_id will be launched into the same client.
                Allowed characters: letters, numbers, "_", "-", "."
            dataset_fpath: Absolute filepath to data.
            permissions: Permissions dict. If not provided, we allow all operations.
            policy: Policy dict. If not provided, we use empty policies.
        """
        self._validate_string("dataset_id", dataset_id)
        self._validate_string("gateway_id", gateway_id)

        if policy is None:
            policy = {}
        if permissions is None:
            permissions = {"any_operation": True}

        if not Path(dataset_fpath).is_file():
            raise FileNotFoundError(
                f"The `dataset_fpath` {dataset_fpath} could not be found."
            )

        # NVFlare executors run with current working directory elsewhere. So we need to
        # resolve relative filepaths
        dataset_fpath = str(Path(dataset_fpath).absolute())

        self.dataset_id = dataset_id
        self.gateway_id = gateway_id
        self.dataset_fpath = dataset_fpath
        self.permissions = permissions
        self.policy = policy

    @staticmethod
    def _validate_string(argument_name: str, argument: str) -> None:
        if not isinstance(argument, str):
            raise ValueError(
                f" For `{argument_name} the expected input type is string. You provided "
                "a value of type {type(argument)}. Please provide a string."
            )
        pattern = "^[A-Za-z0-9_.-]*$"
        valid = bool(re.match(pattern, argument))
        if not valid:
            raise ValueError(
                f"The argument {argument_name} should only consist of letters, numbers, "
                f"'_', '.' and '-'. You provided the value {argument}."
            )
