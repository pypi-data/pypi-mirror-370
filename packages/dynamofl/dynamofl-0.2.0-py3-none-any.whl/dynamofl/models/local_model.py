"""DynamoFL local model"""
import logging

import shortuuid

from ..entities.model import LocalModelEntity
from ..file_transfer.upload_v2 import (
    FileUploaderV2,
    MultipartFileUploadResponse,
    ParamsArgsV2,
    UploadedFile,
)
from ..Helpers import FileUtils
from ..models.model import Model
from ..Request import _Request

try:
    from typing import List, Optional
except ImportError:
    from typing_extensions import List, Optional

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024 * 1024  # 1MB
VALID_MODEL_EXTENSIONS = [".pt", ".bin", ".safetensors"]
VALID_ZIP_EXTENSIONS = [".zip"]


class LocalModel(Model):
    """LocalModel"""

    def __init__(self, request, name: str, key: str, model_id: str, config, size: int) -> None:
        self.request = request
        self.size = size
        super().__init__(
            request=request,
            name=name,
            key=key,
            config=config,
            model_type="LOCAL",
            model_id=model_id,
        )

    @staticmethod
    def create_and_upload(
        request: _Request,
        name: str,
        architecture: Optional[str],
        key: Optional[str],
        model_file_path: Optional[str],
        model_file_paths: Optional[List[str]],
        checkpoint_json_file_path: Optional[str],
        architecture_hf_token: Optional[str],
        model_folder_zip_path: Optional[str],
        peft_config_path: Optional[str] = None,
    ) -> LocalModelEntity:
        LocalModel.validate_model_file_paths(
            model_file_path=model_file_path,
            model_file_paths=model_file_paths,
            checkpoint_json_file_path=checkpoint_json_file_path,
            model_folder_zip_path=model_folder_zip_path,
        )

        if not (architecture or model_folder_zip_path):
            raise ValueError("One of architecture or model_folder_zip_path must be provided")

        if not architecture and architecture_hf_token:
            logger.warning("Ignoring architecture_hf_token as architecture is not provided")

        model_entity_key = shortuuid.uuid() if not key else key
        model_file_size = 0
        config = {}

        if model_folder_zip_path:
            uploaded_model_file: UploadedFile = LocalModel.upload_model_file(
                request=request, key=model_entity_key, model_file_path=model_folder_zip_path
            )
            config["modelFolderZipS3Key"] = uploaded_model_file.object_key
            model_file_size = uploaded_model_file.file_size

        else:
            model_ckpts_keys = []
            model_file_paths = model_file_paths if model_file_paths else []
            if model_file_path:
                model_file_paths.append(model_file_path)

            for model_path in model_file_paths:
                uploaded_model_file: UploadedFile = LocalModel.upload_model_file(
                    request=request, key=model_entity_key, model_file_path=model_path
                )
                model_ckpts_keys.append(uploaded_model_file.object_key)
                model_file_size += uploaded_model_file.file_size

            if checkpoint_json_file_path:
                uploaded_model_file: UploadedFile = LocalModel.upload_model_file(
                    request=request, key=model_entity_key, model_file_path=checkpoint_json_file_path
                )
                config["checkpointJsonS3Key"] = uploaded_model_file.object_key

            config["objKeys"] = model_ckpts_keys
            config["model_architecture"] = architecture
            if architecture_hf_token:
                config["hf_token"] = architecture_hf_token

            if peft_config_path:
                config["peftConfigS3Key"] = LocalModel.upload_peft_file(
                    request=request, peft_config_path=peft_config_path
                )

        model_id = Model.create_ml_model_and_get_id(
            request=request,
            name=name,
            key=model_entity_key,
            model_type="LOCAL",
            config=config,
            size=model_file_size,
        )

        return LocalModelEntity(
            id=model_id,
            name=name,
            key=model_entity_key,
            config=config,
            size=model_file_size,
            api_host=request.host,
        )

    @staticmethod
    def validate_model_file_paths(
        model_file_path: Optional[str],
        model_file_paths: Optional[List[str]],
        checkpoint_json_file_path: Optional[str],
        model_folder_zip_path: Optional[str],
    ):
        if model_folder_zip_path is None and model_file_path is None and model_file_paths is None:
            raise ValueError(
                "Validation Error: Either model_file_path or model_file_paths or model_folder_zip_path must be provided"
            )

        if model_folder_zip_path is not None:
            if (
                model_file_path is not None
                or model_file_paths is not None
                or checkpoint_json_file_path is not None
            ):
                raise ValueError(
                    "Validation Error: If model_folder_zip_path is provided, "
                    "model_file_path, model_file_paths and checkpoint_json_file_path "
                    "should not be there"
                )
            FileUtils.validate_file_extension(
                model_folder_zip_path, VALID_ZIP_EXTENSIONS, "Model folder zip file:"
            )

        if model_file_path is not None:
            if model_file_paths is not None or checkpoint_json_file_path is not None:
                raise ValueError(
                    "Validation Error: If model_file_path is provided, "
                    "model_file_paths and checkpoint_json_file_path "
                    "should not be there"
                )
            FileUtils.validate_file_extension(
                model_file_path, VALID_MODEL_EXTENSIONS, "Model file:"
            )

        if model_file_paths is not None:
            if len(model_file_paths) <= 1 or checkpoint_json_file_path is None:
                raise ValueError(
                    "Validation Error: If model_file_paths is provided,"
                    " its size must be > 1 and checkpoint_json_file_path must be "
                    "provided for it"
                )
            FileUtils.validate_file_extension(
                checkpoint_json_file_path, [".json"], "Checkpoint file:"
            )
            for file_path in model_file_paths:
                FileUtils.validate_file_extension(file_path, VALID_MODEL_EXTENSIONS, "Model file:")

    @staticmethod
    def upload_peft_file(request: _Request, peft_config_path) -> str:
        response: UploadedFile = LocalModel.upload_model_file(
            request=request, key=None, model_file_path=peft_config_path
        )
        return response.object_key

    @staticmethod
    def upload_model_file(
        request: _Request, key: Optional[str], model_file_path: str
    ) -> UploadedFile:
        def construct_params_v2(params_args: ParamsArgsV2):
            params = {
                "filename": params_args.filename,
                "parts": params_args.parts,
            }
            if key:
                params["key"] = key
            return params

        file_uploader_v2 = FileUploaderV2(request)
        response_v2: MultipartFileUploadResponse = file_uploader_v2.multipart_upload(
            file_path=model_file_path,
            presigned_endpoint_url="/ml-model/multipart-presigned-urls",
            construct_params=construct_params_v2,
        )
        return UploadedFile(
            object_key=response_v2.multipart_upload.obj_key,
            entity_key=response_v2.multipart_upload.entity_key,
            file_size=response_v2.file_metadata.size,
        )

    @staticmethod
    def create_hf_model(
        request: _Request,
        name: str,
        hf_id: str,
        is_peft: bool,
        architecture_hf_id: Optional[str] = None,
        hf_token: Optional[str] = None,
        key: Optional[str] = None,
    ) -> LocalModelEntity:
        model_entity_key = shortuuid.uuid() if not key else key

        config = {
            "is_hf_model": True,
            "model_ckpt": hf_id,
            "hf_token": hf_token,
            "is_peft": is_peft,
            "model_architecture": architecture_hf_id,
        }
        model_id = Model.create_ml_model_and_get_id(
            request=request,
            name=name,
            key=model_entity_key,
            model_type="LOCAL",
            config=config,
        )

        return LocalModelEntity(
            id=model_id,
            name=name,
            key=model_entity_key,
            config=config,
            api_host=request.host,
        )

    @staticmethod
    def create_hf_guardrail_model(
        request: _Request,
        name: str,
        model_id: str,
        hf_token: str,
        key: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> LocalModelEntity:
        model_entity_key = shortuuid.uuid() if not key else key

        config = {
            "model_id": model_id,
            "hf_token": hf_token,
            "system_prompt": system_prompt,
            "api_type": "hf_guardrail",
        }
        # Unsure how to implement this correctly.
        model_id = Model.create_ml_model_and_get_id(
            request=request,
            name=name,
            key=model_entity_key,
            model_type="LOCAL_GUARDRAIL",
            config=config,
        )

        return LocalModelEntity(
            id=model_id,
            name=name,
            key=model_entity_key,
            config=config,
            api_host=request.host,
        )
