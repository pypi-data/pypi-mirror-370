import logging
import os
from typing import Any

import requests
from requests import HTTPError

EARLIEST_SUPPORTED_DV_VERSION = "2024.1"
SUPPORTED_BUILD_MODELS = {
    "2024.1": [
        "gradle-attributes",
        "gradle-build-cache-performance",
        "gradle-projects",
        "gradle-network-activity",
        "gradle-artifact-transform-executions",
        "gradle-deprecations",
        "maven-attributes",
        "maven-build-cache-performance",
        "maven-modules",
        "maven-dependency-resolution",
    ],
    "2024.2": [
        "gradle-attributes",
        "gradle-build-cache-performance",
        "gradle-projects",
        "gradle-network-activity",
        "gradle-artifact-transform-executions",
        "gradle-deprecations",
        "gradle-plugins",
        "gradle-resource-usage",
        "gradle-build-profile-overview",
        "gradle-configuration-cache",
        "maven-attributes",
        "maven-build-cache-performance",
        "maven-modules",
        "maven-dependency-resolution",
        "maven-plugins",
        "maven-resource-usage",
        "maven-build-profile-overview",
        "bazel-attributes",
        "bazel-critical-path",
    ],
    "2024.3": [
        "gradle-artifact-transform-executions",
        "gradle-attributes",
        "gradle-build-cache-performance",
        "gradle-build-profile-overview",
        "gradle-configuration-cache",
        "gradle-deprecations",
        "gradle-dependencies",
        "gradle-network-activity",
        "gradle-plugins",
        "gradle-projects",
        "gradle-resource-usage",
        "gradle-test-performance",
        "maven-attributes",
        "maven-build-cache-performance",
        "maven-build-profile-overview",
        "maven-dependencies",
        "maven-dependency-resolution",
        "maven-modules",
        "maven-plugins",
        "maven-resource-usage",
        "maven-test-performance",
        "bazel-attributes",
        "bazel-critical-path",
        "npm-attributes",
        "python-attributes",
    ],
    "2025.1": [
        "gradle-artifact-transform-executions",
        "gradle-attributes",
        "gradle-build-cache-performance",
        "gradle-build-profile-overview",
        "gradle-configuration-cache",
        "gradle-deprecations",
        "gradle-dependencies",
        "gradle-network-activity",
        "gradle-plugins",
        "gradle-projects",
        "gradle-resource-usage",
        "gradle-test-performance",
        "maven-attributes",
        "maven-build-cache-performance",
        "maven-build-profile-overview",
        "maven-dependencies",
        "maven-dependency-resolution",
        "maven-modules",
        "maven-plugins",
        "maven-resource-usage",
        "maven-test-performance",
        "bazel-attributes",
        "bazel-critical-path",
        "npm-attributes",
        "python-attributes",
        "sbt-attributes",
    ],
    "2025.2": [
        "gradle-artifact-transform-executions",
        "gradle-attributes",
        "gradle-build-cache-performance",
        "gradle-build-profile-overview",
        "gradle-configuration-cache",
        "gradle-deprecations",
        "gradle-dependencies",
        "gradle-network-activity",
        "gradle-plugins",
        "gradle-projects",
        "gradle-resource-usage",
        "gradle-test-performance",
        "maven-attributes",
        "maven-build-cache-performance",
        "maven-build-profile-overview",
        "maven-dependencies",
        "maven-dependency-resolution",
        "maven-modules",
        "maven-plugins",
        "maven-resource-usage",
        "maven-test-performance",
        "bazel-attributes",
        "bazel-critical-path",
        "npm-attributes",
        "python-attributes",
        "sbt-attributes",
    ],
}


def _get_env_var_or_fail(var_name: str) -> str:
    if var_name not in os.environ:
        raise EnvironmentError(f"The environment variable {var_name} is not set!")
    return os.environ[var_name]


def get_develocity_server() -> str:
    return _get_env_var_or_fail("DEVELOCITY_SERVER")


def get_develocity_access_key() -> str:
    return _get_env_var_or_fail("DEVELOCITY_API_KEY")


class DevelocityVersion:
    def __init__(self, version: str):
        if version < EARLIEST_SUPPORTED_DV_VERSION:
            raise EnvironmentError(
                f"Develocity version {version} is unsupported! This server only works with Develocity versions greater than or equal to {EARLIEST_SUPPORTED_DV_VERSION}."
            )
        self.version_num = version

    def get_supported_build_models(self):
        return SUPPORTED_BUILD_MODELS[self.version_num]


class DevelocityMCPServerConfig:
    def __init__(self, allow_untrusted_server: bool) -> None:
        self.server_url = get_develocity_server()
        self.access_key = get_develocity_access_key()
        self.verify_requests = not allow_untrusted_server
        if "DEVELOCITY_VERSION" in os.environ:
            self.dv_version = DevelocityVersion(os.environ["DEVELOCITY_VERSION"])
        else:
            self.dv_version = self._get_develocity_version_from_server()

    @staticmethod
    def _parse_version_number(response: dict[str, Any]) -> str:
        return ".".join(response["string"].split(".")[:2])  # removes minor version if present

    def _get_develocity_version_from_server(self) -> DevelocityVersion:
        api_url = f"{self.server_url}/api/version"
        headers = {"Authorization": f"Bearer {self.access_key}", "Accept": "application/json"}
        try:
            resp = requests.get(api_url, headers=headers, timeout=30, verify=self.verify_requests)
            if resp.status_code != 200:
                raise HTTPError(f"Error sending request to {api_url}: {resp.status_code} - {resp.text}")
            version_num = self._parse_version_number(resp.json())
            logging.debug(f"Develocity version number: {version_num}")
            return DevelocityVersion(version_num)
        except HTTPError as e:
            raise e
        except Exception:
            raise RuntimeError(f"Error getting develocity version from {self.server_url}!")
