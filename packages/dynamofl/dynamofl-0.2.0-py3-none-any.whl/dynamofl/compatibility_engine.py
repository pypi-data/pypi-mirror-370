"""
    This module is used to check the compatibility of the client version with the server version.
"""

import logging
import re

import pkg_resources


class CompatibilityEngine:
    """
    This class is used to check the compatibility of the client version with the server version.
    """

    dev_version = "dev"
    compatible_minor_versions = [
        "3.21",
        "3.22",
        "3.23",
    ]

    def __init__(self):
        self.client_version = pkg_resources.get_distribution("dynamofl").version
        self.logger = logging.getLogger(__name__)
        self.logger.info("Client version: %s", self.client_version)

    @staticmethod
    def _validate_server_version_format(server_version: str):
        """
        The server version should be in the format of "X.Y.Z" where
            - X is the major version
            - Y is the minor version
            - Z is the patch version
        Now, there could be a case where we have X.Y.Z.A as well in case of hotfix
        """
        if not re.match(r"^\d+\.\d+\.\d+(\.\d+)?$", server_version):
            raise ValueError(f"Invalid server version format: {server_version}")

    @staticmethod
    def _is_compatible(server_version: str) -> bool:
        server_version_parts = server_version.split(".")
        server_major_version, server_minor_version = (
            server_version_parts[0],
            server_version_parts[1],
        )
        return (
            f"{server_major_version}.{server_minor_version}"
            in CompatibilityEngine.compatible_minor_versions
        )

    def validate_version_compatibility(self, server_version: str | None):
        if server_version is None:
            self.logger.warning(
                "Server version API is not available, skipping version compatibility check"
            )
            return

        if server_version == self.dev_version:
            self.logger.warning(
                "Server version is dev version, skipping version compatibility check"
            )
            return

        self._validate_server_version_format(server_version)

        if not self._is_compatible(server_version):
            raise ValueError(
                f"Client version {self.client_version} is not compatible with DynamoAI server version {server_version}\n"
                "Please refer to the documentation at https://pypi.org/project/dynamofl/ to install the correct version "
                "of the sdk which is compatible with your server version"
            )
        else:
            self.logger.info(
                "Client version %s is compatible with server version %s",
                self.client_version,
                server_version,
            )
