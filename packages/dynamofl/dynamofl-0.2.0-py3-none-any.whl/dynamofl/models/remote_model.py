"""DynamoFL Remote Model"""
import shortuuid

from ..entities.model import RemoteModelEntity
from ..models.model import Model
from ..Request import _Request

try:
    from typing import Optional
except ImportError:
    from typing_extensions import Optional


class RemoteModel(Model):
    """RemoteModel"""

    def __init__(
        self,
        request,
        name: str,
        key: str,
        model_id: str,
        config,
    ) -> None:
        self.request = request
        super().__init__(
            request=request,
            name=name,
            key=key,
            config=config,
            model_type="REMOTE",
            model_id=model_id,
        )

    @staticmethod
    def create(
        request: _Request,
        name: str,
        key: str,
        config: object,
    ) -> RemoteModelEntity:
        model_id = Model.create_ml_model_and_get_id(
            request=request, name=name, key=key, model_type="REMOTE", config=config, size=None
        )
        return RemoteModelEntity(
            id=model_id,
            name=name,
            key=key,
            config=config,
            api_host=request.host,
        )

    @staticmethod
    def create_azure_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        model_endpoint: str,
        api_version: Optional[str] = None,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "azure",
            "remoteModelApiInstance": api_instance,
            "remoteModelEndpoint": model_endpoint,
            "apiVersion": api_version,
            "apiKey": api_key,
        }

        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_lambdalabs_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        model_endpoint: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "lambdalabs",
            "remoteModelApiInstance": api_instance,
            "remoteModelEndpoint": model_endpoint,
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_openai_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "openai",
            "remoteModelApiInstance": api_instance,
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_anthropic_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "anthropic",
            "remoteModelApiInstance": api_instance,
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_mistral_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "mistral",
            "remoteModelApiInstance": api_instance,
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_togetherai_model(
        request: _Request,
        name: str,
        api_instance: str,
        api_key: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "togetherai",
            "remoteModelApiInstance": api_instance,
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_databricks_model(
        request: _Request,
        name: str,
        api_key: str,
        model_endpoint: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "databricks",
            "remoteModelEndpoint": model_endpoint,
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key
        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_custom_model(
        request: _Request,
        name: str,
        remote_model_endpoint: str,
        remote_api_auth_config: dict,
        request_transformation_expression: Optional[str] = None,
        response_transformation_expression: Optional[str] = None,
        response_type: Optional[str] = "string",
        batch_size: Optional[int] = 1,
        multi_turn_support: Optional[bool] = True,
        enable_retry: Optional[bool] = False,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "custom_model",
            "remoteModelEndpoint": remote_model_endpoint,
            "remoteApiAuthConfig": remote_api_auth_config,
            "customApiLMConfig": {
                "request_transformation_expression": request_transformation_expression,
                "response_transformation_expression": response_transformation_expression,
                "response_type": response_type,
                "batch_size": batch_size,
                "multi_turn_support": multi_turn_support,
                "enable_retry": enable_retry,
            },
        }
        model_entity_key = shortuuid.uuid() if not key else key
        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_guardrail_model(
        request: _Request,
        name: str,
        api_key: str,
        model_endpoint: str,
        policy_id: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "guardrail",
            "remoteModelEndpoint": model_endpoint,
            "metadata": {
                "policy_id": policy_id,
            },
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key
        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)
