"""Entities for Custom Rag app and their routes"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from dataclasses_json import LetterCase, dataclass_json

logger = logging.getLogger(__name__)


class AuthTypeEnum(Enum):
    API_KEY = "api_key"
    BEARER = "bearer"
    CLIENT_CERTIFICATE = "client_certificate"
    NO_AUTH = "no_auth"
    OAUTH = "oauth"


class RouteTypeEnum(Enum):
    RETRIEVE = "retrieve"


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class CustomRagApplicationRoutesEntity:
    """Custom Rag Application Route Entity"""

    route_type: RouteTypeEnum
    route_path: str
    request_transformation_expression: Optional[str] = None
    response_transformation_expression: Optional[str] = None
    custom_rag_application_id: Optional[int] = None


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass(kw_only=True)
class CustomRagApplicationRoutesResponseEntity(CustomRagApplicationRoutesEntity):
    """Custom Rag Application Route Response Entity"""

    route_id: int


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class CustomRagApplicationEntity:
    """Custom Rag Application Entity"""

    base_url: str
    auth_type: AuthTypeEnum
    auth_config: Optional[Dict[str, Any]] = None
    custom_rag_application_routes: Optional[List[CustomRagApplicationRoutesEntity]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass(kw_only=True)
class CustomRagApplicationResponseEntity(CustomRagApplicationEntity):
    """Custom Rag Application Response Entity"""

    custom_rag_application_id: int
    custom_rag_application_routes: Optional[List[CustomRagApplicationRoutesResponseEntity]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class AllCustomRagApplicationResponseEntity:
    """Entity for all Custom Rag Applications"""

    total: int
    custom_rag_application_entities: List[CustomRagApplicationResponseEntity]
