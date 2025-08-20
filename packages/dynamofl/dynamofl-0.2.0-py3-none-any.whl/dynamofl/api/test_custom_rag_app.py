# pylint: disable=protected-access
"""Tests for the CustomRagAPI class."""

import json
from typing import Optional
from unittest.mock import Mock

import pytest
from dynamofl.api.custom_rag_app import CustomRagAPI
from dynamofl.entities.custom_rag_app import (
    AllCustomRagApplicationResponseEntity,
    AuthTypeEnum,
    CustomRagApplicationEntity,
    CustomRagApplicationResponseEntity,
    CustomRagApplicationRoutesEntity,
    CustomRagApplicationRoutesResponseEntity,
    RouteTypeEnum,
)


@pytest.fixture(name="mock_request")
def mock_request_fixture():
    mock = Mock()
    mock._make_request = Mock()
    return mock


@pytest.fixture(name="custom_rag_api")
def custom_rag_api_fixture(mock_request):
    return CustomRagAPI(mock_request)


def test_create(custom_rag_api, mock_request):
    base_url = "http://example.com"
    auth_type = AuthTypeEnum.NO_AUTH
    auth_config = None
    custom_rag_application_routes = None
    custom_rag_application_id = 1

    mock_response = get_mock_response(
        base_url=base_url,
        auth_type=auth_type,
        include_auth_config=bool(auth_config),
        include_custom_rag_application_routes=bool(custom_rag_application_routes),
    )
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.create(
        base_url=base_url,
        auth_type=auth_type,
        auth_config=auth_config,
        custom_rag_application_routes=custom_rag_application_routes,
    )
    assert isinstance(result, CustomRagApplicationResponseEntity)
    assert result.custom_rag_application_id == custom_rag_application_id
    assert result.base_url == base_url
    assert result.auth_type == auth_type
    mock_request._make_request.assert_called_once_with(
        "POST",
        "/custom-rag-application",
        params=get_mock_request(
            base_url=base_url,
            auth_type=auth_type,
            include_auth_config=bool(auth_config),
            include_custom_rag_application_routes=bool(custom_rag_application_routes),
        ),
    )


def test_create_with_auth(custom_rag_api, mock_request):
    base_url = "http://example.com"
    auth_type = AuthTypeEnum.API_KEY
    auth_config = {"api_key": "test_key"}
    custom_rag_application_routes = None
    custom_rag_application_id = 1

    mock_response = get_mock_response(auth_type=auth_type, include_auth_config=True)
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.create(
        base_url=base_url,
        auth_type=auth_type,
        auth_config=auth_config,
        custom_rag_application_routes=custom_rag_application_routes,
    )
    assert isinstance(result, CustomRagApplicationResponseEntity)
    assert result.custom_rag_application_id == custom_rag_application_id
    assert result.base_url == base_url
    assert result.auth_type == auth_type
    assert result.auth_config == auth_config
    mock_request._make_request.assert_called_once_with(
        "POST",
        "/custom-rag-application",
        params=get_mock_request(auth_type=auth_type, include_auth_config=True),
    )


def test_create_with_routes(custom_rag_api, mock_request):
    base_url = "http://example.com"
    auth_type = AuthTypeEnum.NO_AUTH
    auth_config = None
    custom_rag_application_id = 1
    routes = [
        CustomRagApplicationRoutesEntity(
            route_type=RouteTypeEnum.RETRIEVE,
            route_path="/test",
            request_transformation_expression=None,
            response_transformation_expression=None,
            custom_rag_application_id=custom_rag_application_id,
        )
    ]

    mock_response = get_mock_response(include_custom_rag_application_routes=True)
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.create(
        base_url=base_url,
        auth_type=auth_type,
        auth_config=auth_config,
        custom_rag_application_routes=routes,
    )
    assert isinstance(result, CustomRagApplicationResponseEntity)
    assert result.custom_rag_application_id == custom_rag_application_id
    assert result.base_url == base_url
    assert result.auth_type == auth_type
    assert result.custom_rag_application_routes is not None
    assert len(result.custom_rag_application_routes) == 1
    assert result.custom_rag_application_routes[0].route_id == 1
    assert result.custom_rag_application_routes[0].route_type == RouteTypeEnum.RETRIEVE
    mock_request._make_request.assert_called_once_with(
        "POST",
        "/custom-rag-application",
        params=get_mock_request(include_custom_rag_application_routes=True),
    )


def test_update(custom_rag_api, mock_request):
    custom_rag_application_id = 1
    base_url = "http://updated.com"
    auth_type = AuthTypeEnum.NO_AUTH
    auth_config = None
    custom_rag_application_routes = None

    mock_response = get_mock_response(base_url=base_url, auth_type=auth_type)
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.update(
        custom_rag_application_id=custom_rag_application_id,
        base_url=base_url,
        auth_type=auth_type,
        auth_config=auth_config,
        custom_rag_application_routes=custom_rag_application_routes,
    )
    assert isinstance(result, CustomRagApplicationResponseEntity)
    assert result.custom_rag_application_id == custom_rag_application_id
    assert result.base_url == base_url
    mock_request._make_request.assert_called_once()


def test_find_all(custom_rag_api, mock_request):
    mock_response = {
        "total": 2,
        "custom_rag_application_entities": [
            get_mock_response(base_url="http://example1.com"),
            get_mock_response(base_url="http://example2.com"),
        ],
    }
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.find_all(include_routes=False)
    assert isinstance(result, AllCustomRagApplicationResponseEntity)
    assert result.total == 2
    assert len(result.custom_rag_application_entities) == 2
    mock_request._make_request.assert_called_once_with(
        "GET", "/custom-rag-application", params={"includeRoutes": False}
    )


def test_find(custom_rag_api, mock_request):
    mock_response = [get_mock_response()]
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.find(custom_rag_application_id=1, include_routes=False)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CustomRagApplicationResponseEntity)
    assert result[0].custom_rag_application_id == 1
    mock_request._make_request.assert_called_once_with(
        "GET", "/custom-rag-application/1?includeRoutes=False"
    )


def test_delete(custom_rag_api, mock_request):
    custom_rag_api.delete(custom_rag_application_id=1)
    mock_request._make_request.assert_called_once_with("DELETE", "/custom-rag-application/1")


def test_create_route(custom_rag_api, mock_request):
    custom_rag_application_id = 1
    route_type = RouteTypeEnum.RETRIEVE
    route_path = "/test"
    request_transformation_expression = None
    response_transformation_expression = None

    mock_response = [
        get_mock_response(include_custom_rag_application_routes=True)["customRagApplicationRoutes"][
            0
        ]
    ]
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.create_route(
        custom_rag_application_id=custom_rag_application_id,
        route_type=route_type,
        route_path=route_path,
        request_transformation_expression=request_transformation_expression,
        response_transformation_expression=response_transformation_expression,
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CustomRagApplicationRoutesResponseEntity)
    assert result[0].route_id == 1
    assert result[0].route_path == route_path
    mock_request._make_request.assert_called_once()


def test_update_route(custom_rag_api, mock_request):
    custom_rag_application_id = 1
    route_id = 1
    route_type = RouteTypeEnum.RETRIEVE
    route_path = "/updated"
    request_transformation_expression = None
    response_transformation_expression = None

    mock_response = get_mock_response(include_custom_rag_application_routes=True)[
        "customRagApplicationRoutes"
    ][0]
    mock_response["route_path"] = route_path
    mock_request._make_request.return_value = mock_response
    result = custom_rag_api.update_route(
        custom_rag_application_id=custom_rag_application_id,
        route_id=route_id,
        route_type=route_type,
        route_path=route_path,
        request_transformation_expression=request_transformation_expression,
        response_transformation_expression=response_transformation_expression,
    )
    assert isinstance(result, CustomRagApplicationRoutesResponseEntity)
    assert result.route_id == route_id
    assert result.route_path == route_path
    mock_request._make_request.assert_called_once()


def test_delete_route(custom_rag_api, mock_request):
    custom_rag_api.delete_route(custom_rag_application_id=1, route_id=1)
    mock_request._make_request.assert_called_once_with(
        "DELETE", "/custom-rag-application/1/route/1"
    )


def test_find_with_empty_response(custom_rag_api, mock_request):
    mock_request._make_request.return_value = None
    result = custom_rag_api.find(custom_rag_application_id=1)
    assert isinstance(result, list)
    assert len(result) == 0


def test_create_route_with_empty_response(custom_rag_api, mock_request):
    custom_rag_application_id = 1
    route_type = RouteTypeEnum.RETRIEVE
    route_path = "/test"

    mock_request._make_request.return_value = None
    result = custom_rag_api.create_route(
        custom_rag_application_id=custom_rag_application_id,
        route_type=route_type,
        route_path=route_path,
    )
    assert isinstance(result, list)
    assert len(result) == 0


def get_mock_request(
    base_url: Optional[str] = None,
    auth_type: Optional[AuthTypeEnum] = None,
    include_auth_config: bool = False,
    include_custom_rag_application_routes: bool = False,
):
    auth_config = {"api_key": "test_key"} if include_auth_config else None
    routes = None
    if include_custom_rag_application_routes:
        routes = [
            CustomRagApplicationRoutesEntity(
                route_type=RouteTypeEnum.RETRIEVE,
                route_path="/test",
                request_transformation_expression=None,
                response_transformation_expression=None,
                custom_rag_application_id=1,
            )
        ]
    custom_rag_app_create = CustomRagApplicationEntity(
        base_url=base_url or "http://example.com",
        auth_type=auth_type or AuthTypeEnum.NO_AUTH,
        auth_config=auth_config,
        custom_rag_application_routes=routes,
    )
    return json.loads(custom_rag_app_create.to_json())  # type: ignore


def get_mock_response(
    base_url: Optional[str] = None,
    auth_type: Optional[AuthTypeEnum] = None,
    include_auth_config: bool = False,
    include_custom_rag_application_routes: bool = False,
):
    auth_config = {"api_key": "test_key"} if include_auth_config else None
    routes = None
    if include_custom_rag_application_routes:
        routes = [
            CustomRagApplicationRoutesResponseEntity(
                route_id=1,
                route_type=RouteTypeEnum.RETRIEVE,
                route_path="/test",
                request_transformation_expression=None,
                response_transformation_expression=None,
                custom_rag_application_id=1,
            )
        ]

    custom_rag_app_response = CustomRagApplicationResponseEntity(
        custom_rag_application_id=1,
        base_url=base_url or "http://example.com",
        auth_type=auth_type or AuthTypeEnum.NO_AUTH,
        auth_config=auth_config,
        custom_rag_application_routes=routes,
    )
    return json.loads(custom_rag_app_response.to_json())  # type: ignore
