""" File uploader using multipart upload """
import logging
from dataclasses import dataclass
from io import BufferedReader, BytesIO
from typing import Any, Callable, Dict, List

import requests
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from ..Request import _Request
from .metadata import FileMetadata
from .multipart_file_uploader_api import (
    MultipartFileUploaderApi,
    MultipartPresignedUrl,
    MultipartUpload,
    ParamsArgsV2,
    UploadedFilePart,
)
from .thread_executor import ThreadedExecutor

logger = logging.getLogger(__name__)


@dataclass
class UploadedFile:
    """Class to hold uploaded file metadata"""

    object_key: str
    entity_key: str
    file_size: int


@dataclass
class FileUploaderConfig:
    """Class to hold configuration for file uploader"""

    threading: bool = True
    size_per_part: int = 500 * 1024 * 1024  # 500 MB
    max_concurrent_uploads: int = 3


@dataclass
class MultipartFileUploadResponse:
    file_metadata: FileMetadata
    multipart_upload: MultipartUpload


class FileUploaderV2:
    """File uploader using multipart upload"""

    def __init__(self, request: _Request):
        logger.debug("Initializing FileUploaderV2.....")
        self.request = request
        self.config = FileUploaderConfig()

    def _upload_file_part(self, chunk, part: MultipartPresignedUrl) -> UploadedFilePart:
        response = requests.put(
            part.url,
            data=chunk,
            timeout=600,
            headers={"x-amz-checksum-sha1": part.sha1_checksum},
            verify=False
        )
        if not response.ok or response.status_code != 200:
            logger.error(
                "Failed to upload file part: %s Presigned Url error %s: %s",
                part.part_number,
                response.status_code,
                response.text,
            )
        response.raise_for_status()
        e_tag = response.headers["ETag"]
        return UploadedFilePart(e_tag, part.part_number, part.sha1_checksum)

    def _multipart_upload_via_threading(
        self, multipart_upload: MultipartUpload, f: BufferedReader, t: tqdm
    ) -> List[UploadedFilePart]:
        logger.debug("Uploading file parts via threading...")
        thread_executor = ThreadedExecutor(self.config.max_concurrent_uploads)
        uploaded_file_parts: List[UploadedFilePart] = []
        try:
            for part in multipart_upload.parts:
                chunk = f.read(self.config.size_per_part)
                wrapped_chunk = CallbackIOWrapper(t.update, BytesIO(chunk), "read")
                thread_executor.submit(self._upload_file_part, wrapped_chunk, part)
            uploaded_file_parts = thread_executor.get_results()
            uploaded_file_parts.sort(key=lambda x: x.part_number)
            return uploaded_file_parts
        except Exception as e:
            logger.error("Failed to upload file parts via threading: %s", e)
            raise e
        finally:
            thread_executor.shutdown()

    def _sequential_multipart_upload(
        self, multipart_upload: MultipartUpload, f: BufferedReader, t: tqdm
    ) -> List[UploadedFilePart]:
        logger.debug("Uploading file parts sequentially...")
        uploaded_file_parts: List[UploadedFilePart] = []
        for part in multipart_upload.parts:
            chunk = f.read(self.config.size_per_part)
            wrapped_chunk = CallbackIOWrapper(t.update, BytesIO(chunk), "read")
            uploaded_file_parts.append(self._upload_file_part(wrapped_chunk, part))
        return uploaded_file_parts

    def multipart_upload(
        self,
        file_path: str,
        presigned_endpoint_url: str,
        construct_params: Callable[[ParamsArgsV2], Dict[str, Any]],
    ):
        logger.info("MultipartUpload: Starting to upload file: %s", file_path)
        file_metadata = FileMetadata(file_path, self.config.size_per_part)
        multipart_uploader_api = MultipartFileUploaderApi(
            self.request, file_metadata, presigned_endpoint_url, construct_params
        )
        multipart_upload = multipart_uploader_api.start()
        entity_key = multipart_upload.entity_key
        upload_id = multipart_upload.upload_id
        uploaded_file_parts: List[UploadedFilePart] = []

        try:
            with open(file_metadata.file_path, "rb") as f:
                with tqdm(
                    total=file_metadata.size, unit="B", unit_scale=True, unit_divisor=1024
                ) as t:
                    if self.config.threading:
                        uploaded_file_parts = self._multipart_upload_via_threading(
                            multipart_upload, f, t
                        )
                    else:
                        uploaded_file_parts = self._sequential_multipart_upload(
                            multipart_upload, f, t
                        )
        except Exception as e:
            logger.error("Failed to upload file: %s", e)
            logger.debug("Aborting multipart upload: %s", upload_id)
            multipart_uploader_api.abort(upload_id, entity_key)
            raise e

        multipart_uploader_api.complete(upload_id, entity_key, uploaded_file_parts)
        logger.info("Successfully uploaded file")
        return MultipartFileUploadResponse(
            file_metadata=file_metadata,
            multipart_upload=multipart_upload,
        )
