"""Dataset class for Dynamofl."""

import csv
import tempfile

from ..file_transfer.upload_v2 import FileUploaderV2, MultipartFileUploadResponse, UploadedFile
from ..Helpers import FileUtils
from ..Request import _Request
from .base_dataset import BaseDataset

CHUNK_SIZE = 1024 * 1024  # 1MB
VALID_DATASET_FILE_EXTENSIONS = [".csv"]


class Dataset(BaseDataset):
    """Dataset class for Dynamofl."""

    def __init__(
        self, request: _Request, name: str, key: str, file_path: str, test_file_path: str
    ) -> None:
        self.request = request
        FileUtils.validate_file_extension(file_path, VALID_DATASET_FILE_EXTENSIONS, "Dataset file:")

        if test_file_path:
            FileUtils.validate_file_extension(
                test_file_path, VALID_DATASET_FILE_EXTENSIONS, "Dataset test file:"
            )
            with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
                tmp_file_path = tmp_file.name
                self._create_train_test_file(file_path, test_file_path, tmp_file_path)
                upload_op: UploadedFile = self.upload_dataset_file(
                    key=key, dataset_file_path=tmp_file_path
                )
        else:
            upload_op: UploadedFile = self.upload_dataset_file(key=key, dataset_file_path=file_path)
        obj_key = upload_op.object_key
        key = upload_op.entity_key
        config = {"objKey": obj_key}

        super().__init__(request=request, name=name, key=key, config=config)

    def upload_dataset_file(self, key: str, dataset_file_path: str) -> UploadedFile:
        file_uploader = FileUploaderV2(self.request)
        response_v2: MultipartFileUploadResponse = file_uploader.multipart_upload(
            file_path=dataset_file_path,
            presigned_endpoint_url="/dataset/multipart-presigned-urls",
            construct_params=lambda params_args: {
                "key": key,
                "parts": params_args.parts,
                "filename": params_args.filename,
            },
        )
        return UploadedFile(
            object_key=response_v2.multipart_upload.obj_key,
            entity_key=response_v2.multipart_upload.entity_key,
            file_size=response_v2.file_metadata.size,
        )

    def _read_csv_add_split(self, file_path, split):
        with open(file_path, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader) + ["split"]
            data = [header] + [row + [split] for row in reader]
        return data

    def _create_train_test_file(
        self, train_file_path: str, test_file_path: str, output_file_path: str
    ) -> None:
        train_data = self._read_csv_add_split(train_file_path, "train")
        test_data = self._read_csv_add_split(test_file_path, "test")

        assert (
            train_data[0] == test_data[0]
        ), "The column names in the train and test files must match"
        combined_data = train_data + test_data[1:]

        with open(output_file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(combined_data)
