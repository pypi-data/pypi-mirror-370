"""Hugging Face Dataset"""
from typing import Optional

from ..entities.dataset import HFDatasetEntity
from ..Request import _Request
from .base_dataset import BaseDataset


class HFDataset(BaseDataset):
    """Hugging Face Dataset"""

    @staticmethod
    def create_dataset(
        request: _Request,
        name: str,
        hf_id: str,
        hf_token: Optional[str] = None,
        key: Optional[str] = None,
    ):
        params = {
            "name": name,
            "key": key,
            "source": "HuggingFace",
            "config": {
                "hfToken": hf_token,
                "hfId": hf_id,
            },
        }
        dataset = BaseDataset.create_dfl_dataset(request, params)
        return HFDatasetEntity(
            name=name,
            hf_id=hf_id,
            hf_token=hf_token,
            id=dataset["_id"],
        )
