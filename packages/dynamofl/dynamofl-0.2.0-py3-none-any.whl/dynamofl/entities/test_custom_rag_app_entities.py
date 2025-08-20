"""Tests for custom RAG application entities."""

import pytest
from dynamofl.entities.custom_rag_app import (
    AllCustomRagApplicationResponseEntity,
    AuthTypeEnum,
    CustomRagApplicationEntity,
    CustomRagApplicationResponseEntity,
    CustomRagApplicationRoutesEntity,
    CustomRagApplicationRoutesResponseEntity,
    RouteTypeEnum,
)

# Constants
TEST_ROUTE_PATH = "/retrieve"
TEST_BASE_URL = "https://example.com"
TEST_AUTH_CONFIG = {"api_key": "test_key"}


def test_custom_rag_application_routes_entity():
    route = CustomRagApplicationRoutesEntity(
        route_type=RouteTypeEnum.RETRIEVE,
        route_path=TEST_ROUTE_PATH,
        request_transformation_expression="request_transformation_expression",
        response_transformation_expression="response_transformation_expression",
        custom_rag_application_id=1,
    )

    assert route.route_type == RouteTypeEnum.RETRIEVE
    assert route.route_path == TEST_ROUTE_PATH
    assert route.request_transformation_expression == "request_transformation_expression"
    assert route.response_transformation_expression == "response_transformation_expression"
    assert route.custom_rag_application_id == 1


def test_custom_rag_application_routes_response_entity():
    route = CustomRagApplicationRoutesResponseEntity(
        route_type=RouteTypeEnum.RETRIEVE, route_path=TEST_ROUTE_PATH, route_id=1
    )

    assert route.route_type == RouteTypeEnum.RETRIEVE
    assert route.route_path == TEST_ROUTE_PATH
    assert route.route_id == 1
    assert route.request_transformation_expression is None
    assert route.response_transformation_expression is None
    assert route.custom_rag_application_id is None


def test_custom_rag_application_entity():
    app = CustomRagApplicationEntity(
        base_url=TEST_BASE_URL,
        auth_type=AuthTypeEnum.API_KEY,
        auth_config=TEST_AUTH_CONFIG,
        custom_rag_application_routes=[
            CustomRagApplicationRoutesEntity(
                route_type=RouteTypeEnum.RETRIEVE, route_path=TEST_ROUTE_PATH
            )
        ],
    )

    assert app.base_url == TEST_BASE_URL
    assert app.auth_type == AuthTypeEnum.API_KEY
    assert app.auth_config == TEST_AUTH_CONFIG
    assert app.custom_rag_application_routes is not None
    assert len(app.custom_rag_application_routes) == 1
    assert isinstance(app.custom_rag_application_routes[0], CustomRagApplicationRoutesEntity)


def test_custom_rag_application_response_entity():
    app = CustomRagApplicationResponseEntity(
        base_url=TEST_BASE_URL,
        auth_type=AuthTypeEnum.API_KEY,
        custom_rag_application_id=1,
        custom_rag_application_routes=[
            CustomRagApplicationRoutesResponseEntity(
                route_type=RouteTypeEnum.RETRIEVE, route_path=TEST_ROUTE_PATH, route_id=1
            )
        ],
    )

    assert app.base_url == TEST_BASE_URL
    assert app.auth_type == AuthTypeEnum.API_KEY
    assert app.custom_rag_application_id == 1
    assert app.custom_rag_application_routes is not None
    assert len(app.custom_rag_application_routes) == 1
    assert isinstance(
        app.custom_rag_application_routes[0], CustomRagApplicationRoutesResponseEntity
    )


def test_all_custom_rag_application_response_entity():
    all_apps = AllCustomRagApplicationResponseEntity(
        total=1,
        custom_rag_application_entities=[
            CustomRagApplicationResponseEntity(
                base_url=TEST_BASE_URL, auth_type=AuthTypeEnum.API_KEY, custom_rag_application_id=1
            )
        ],
    )

    assert all_apps.total == 1
    assert len(all_apps.custom_rag_application_entities) == 1
    assert isinstance(
        all_apps.custom_rag_application_entities[0], CustomRagApplicationResponseEntity
    )


def test_enum_validation():
    with pytest.raises(ValueError):
        CustomRagApplicationEntity(
            base_url=TEST_BASE_URL, auth_type=AuthTypeEnum("invalid_auth_type")
        )

    with pytest.raises(ValueError):
        CustomRagApplicationRoutesEntity(
            route_type=RouteTypeEnum("invalid_route_type"), route_path=TEST_ROUTE_PATH
        )
