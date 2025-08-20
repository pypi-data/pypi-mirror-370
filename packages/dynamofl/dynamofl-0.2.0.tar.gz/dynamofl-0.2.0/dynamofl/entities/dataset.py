""" Dataset entity """
from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseDatasetEntity:
    """Base Entity class for all datasets."""

    _id: str
    id: str
    name: str

    def __init__(self, name: str, id: str) -> None:  # pylint: disable=redefined-builtin
        self._id = id
        self.id = id
        self.name = name


@dataclass
class LocalDatasetEntity(BaseDatasetEntity):
    """Local Dataset entity"""

    key: str

    def __init__(self, name: str, key: str, id: str) -> None:  # pylint: disable=redefined-builtin
        self.key = key
        super().__init__(name, id)


@dataclass
class HFDatasetEntity(BaseDatasetEntity):
    """Hugging Face Dataset entity"""

    hf_id: str
    hf_token: Optional[str]

    def __init__(  # pylint: disable=redefined-builtin
        self, name: str, hf_id: str, hf_token: Optional[str], id: str
    ) -> None:
        self.hf_id = hf_id
        self.hf_token = hf_token
        super().__init__(name, id)
