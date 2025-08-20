"""Base class for all datasets."""
import logging

from ..Request import _Request


class BaseDataset:
    """Base class for all datasets."""

    # TODO: Have inheriting classes use create method instead of relying on __init__
    # for dataset creation via API
    def __init__(
        self,
        request,
        key,
        name,
        config,
    ) -> None:
        self.key = key
        self.name = name
        self.request = request
        self.logger = logging.getLogger("BaseDataset")
        params = {"key": key, "name": name, "config": config, "source": "Local"}
        created_dataset = self.request._make_request("POST", "/dataset", params=params)
        self._id = created_dataset["_id"]
        self.logger.info("Dataset created: %s", created_dataset)

    @staticmethod
    def create_dfl_dataset(request: _Request, params):
        return request._make_request(  # pylint: disable=protected-access
            "POST", "/dataset", params=params
        )
