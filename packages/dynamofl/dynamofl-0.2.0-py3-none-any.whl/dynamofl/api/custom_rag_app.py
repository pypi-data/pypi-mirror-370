""" Module for Custom Rag Adapter APIs """
import json
import logging
from typing import Any, Dict, List, Optional

from ..entities.custom_rag_app import (
    AllCustomRagApplicationResponseEntity,
    AuthTypeEnum,
    CustomRagApplicationEntity,
    CustomRagApplicationResponseEntity,
    CustomRagApplicationRoutesEntity,
    CustomRagApplicationRoutesResponseEntity,
    RouteTypeEnum,
)
from ..Request import _Request

logger = logging.getLogger("CustomRagApplicationAPI")


# pylint: disable=protected-access
class CustomRagAPI:
    """Class for Custom Rag Adapter APIs"""

    def __init__(self, request: _Request):
        self.request = request

    def create(
        self,
        base_url: str,
        auth_type: AuthTypeEnum,
        auth_config: Optional[Dict[str, Any]] = None,
        custom_rag_application_routes: Optional[List[CustomRagApplicationRoutesEntity]] = None,
    ) -> CustomRagApplicationResponseEntity:
        create_custom_rag_app_entity = CustomRagApplicationEntity(
            base_url=base_url,
            auth_type=auth_type,
            auth_config=auth_config,
            custom_rag_application_routes=custom_rag_application_routes,
        )
        entity_dict = json.loads(create_custom_rag_app_entity.to_json())  # type: ignore
        res = self.request._make_request("POST", "/custom-rag-application", params=entity_dict)
        return CustomRagApplicationResponseEntity.from_json(json.dumps(res))  # type: ignore

    def update(
        self,
        custom_rag_application_id: int,
        base_url: str,
        auth_type: AuthTypeEnum,
        auth_config: Optional[Dict[str, Any]] = None,
        custom_rag_application_routes: Optional[List[CustomRagApplicationRoutesEntity]] = None,
    ) -> CustomRagApplicationResponseEntity:
        update_custom_rag_app_entity = CustomRagApplicationEntity(
            base_url=base_url,
            auth_type=auth_type,
            auth_config=auth_config,
            custom_rag_application_routes=custom_rag_application_routes,
        )
        entity_dict = json.loads(update_custom_rag_app_entity.to_json())  # type: ignore
        res = self.request._make_request(
            "PUT",
            f"/custom-rag-application/{custom_rag_application_id}",
            params=entity_dict,
        )
        return CustomRagApplicationResponseEntity.from_json(json.dumps(res))  # type: ignore
        # return map_camel_case_to_snake_case(res, CustomRagApplicationResponseEntity)

    def find_all(self, include_routes: bool = False) -> AllCustomRagApplicationResponseEntity:
        res = self.request._make_request(
            "GET", "/custom-rag-application", params={"includeRoutes": include_routes}
        )
        return AllCustomRagApplicationResponseEntity.from_json(json.dumps(res))  # type: ignore

    def find(
        self, custom_rag_application_id: int, include_routes: bool = False
    ) -> List[CustomRagApplicationResponseEntity]:
        res = self.request._make_request(
            "GET",
            f"/custom-rag-application/{custom_rag_application_id}?includeRoutes={include_routes}",
        )
        if res is None:
            res = []
        processed_res = [
            CustomRagApplicationResponseEntity.from_json(json.dumps(item))  # type: ignore
            for item in res
        ]
        return processed_res

    def delete(self, custom_rag_application_id: int) -> None:
        return self.request._make_request(
            "DELETE", f"/custom-rag-application/{custom_rag_application_id}"
        )

    def create_route(
        self,
        custom_rag_application_id: int,
        route_type: RouteTypeEnum,
        route_path: str,
        request_transformation_expression: Optional[str] = None,
        response_transformation_expression: Optional[str] = None,
    ) -> List[CustomRagApplicationRoutesResponseEntity]:
        create_custom_rag_app_route_entity = CustomRagApplicationRoutesEntity(
            route_type=route_type,
            route_path=route_path,
            request_transformation_expression=request_transformation_expression,
            response_transformation_expression=response_transformation_expression,
            custom_rag_application_id=custom_rag_application_id,
        )
        entity_dict = json.loads(create_custom_rag_app_route_entity.to_json())  # type: ignore
        res = self.request._make_request(
            "POST",
            f"/custom-rag-application/{custom_rag_application_id}/routes",
            params=[entity_dict],
        )
        if res is None:
            res = []
        processed_res = [
            CustomRagApplicationRoutesResponseEntity.from_json(json.dumps(item))  # type: ignore
            for item in res
        ]
        return processed_res

    def update_route(
        self,
        custom_rag_application_id: int,
        route_id: int,
        route_type: RouteTypeEnum,
        route_path: str,
        request_transformation_expression: Optional[str] = None,
        response_transformation_expression: Optional[str] = None,
    ) -> CustomRagApplicationRoutesResponseEntity:
        update_custom_rag_app_route_entity = CustomRagApplicationRoutesEntity(
            route_type=route_type,
            route_path=route_path,
            request_transformation_expression=request_transformation_expression,
            response_transformation_expression=response_transformation_expression,
            custom_rag_application_id=custom_rag_application_id,
        )
        entity_dict = json.loads(update_custom_rag_app_route_entity.to_json())  # type: ignore
        res = self.request._make_request(
            "PUT",
            f"/custom-rag-application/{custom_rag_application_id}/route/{route_id}",
            params=entity_dict,
        )
        return CustomRagApplicationRoutesResponseEntity.from_json(json.dumps(res))  # type: ignore

    def delete_route(self, custom_rag_application_id: int, route_id: int) -> None:
        return self.request._make_request(
            "DELETE",
            f"/custom-rag-application/{custom_rag_application_id}/route/{route_id}",
        )
