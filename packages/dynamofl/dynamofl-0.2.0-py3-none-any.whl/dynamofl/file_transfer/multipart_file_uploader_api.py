""" Class to make requests for starting, aborting and completing multipart upload """
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from ..Request import _Request
from .metadata import FileMetadata

logger = logging.getLogger(__name__)


@dataclass
class MultipartPresignedUrl:
    """Class to hold presigned url and part number for a part of the file"""

    url: str
    part_number: int
    sha1_checksum: str


@dataclass
class MultipartUpload:
    """Class to hold upload id, entity key and presigned urls for all parts of the file"""

    upload_id: str
    entity_key: str
    obj_key: str
    parts: List[MultipartPresignedUrl]


@dataclass
class ParamsArgsV2:
    """Class to hold parameters for constructing params for multipart upload api"""

    filename: str
    parts: List[dict[str, Any]]


@dataclass
class UploadedFilePart:
    """Class to hold e_tag and part number for a part of the file"""

    e_tag: str
    part_number: int
    sha1_checksum: str


class MultipartFileUploaderApi:
    """Class to make requests for starting, aborting and completing multipart upload"""

    def __init__(
        self,
        request: _Request,
        file_metadata: FileMetadata,
        presigned_url_endpoint: str,
        construct_params: Callable[[ParamsArgsV2], Dict[str, Any]],
    ):
        self.request = request
        self.file_metadata = file_metadata
        self.construct_params = construct_params
        self.presigned_url_endpoint = presigned_url_endpoint
        self.abort_url = f"{presigned_url_endpoint}/abort"
        self.complete_url = f"{presigned_url_endpoint}/complete"

    def start(self) -> MultipartUpload:
        parts = [
            {"partNumber": part.part_number, "sha1Checksum": part.sha1_checksum}
            for part in self.file_metadata.parts
        ]
        params = self.construct_params(ParamsArgsV2(filename=self.file_metadata.name, parts=parts))
        # TODO: change _make_request -> make_request as it's being used outside of the class
        # pylint: disable=protected-access
        logger.debug(
            "Sending multipart upload request to api: %s to url: %s",
            params,
            self.presigned_url_endpoint,
        )
        res = self.request._make_request("POST", self.presigned_url_endpoint, params)
        if not res:
            # pylint: disable=broad-exception-raised
            raise Exception("Starting presigned url request failed")
        upload_id = res["uploadId"]
        entity_key = res["entityKey"]
        obj_key = res["objKey"]
        parts = [
            MultipartPresignedUrl(part["url"], part["partNumber"], part["sha1Checksum"])
            for part in res["parts"]
        ]
        return MultipartUpload(upload_id, entity_key, obj_key, parts)

    def abort(self, upload_id: str, entity_key: str):
        params = {
            "uploadId": upload_id,
            "filename": self.file_metadata.name,
            "entityKey": entity_key,
        }
        # pylint: disable=protected-access
        self.request._make_request("POST", self.abort_url, params)

    def complete(self, upload_id: str, entity_key: str, parts: List[UploadedFilePart]):
        uploaded_parts = [
            {"eTag": part.e_tag, "partNumber": part.part_number, "sha1Checksum": part.sha1_checksum}
            for part in parts
        ]
        params = {
            "uploadId": upload_id,
            "filename": self.file_metadata.name,
            "sha1Checksum": self.file_metadata.sha1_checksum,
            "entityKey": entity_key,
            "parts": uploaded_parts,
        }
        # pylint: disable=protected-access
        self.request._make_request("POST", self.complete_url, params)
