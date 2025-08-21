from typing import Any

import requests
from annotations.types import (
    AdvancedSearchQuery,
    BuildId,
    BuildModels,
    IncludeFailedTestsOption,
    IncludeFlakyTestsOption,
    IncludePTSNotSelectedTestsOption,
    IncludeSkippedTestsOption,
    IncludeSuccessfulTestsOption,
    TestContainer,
)
from config import (
    EARLIEST_SUPPORTED_DV_VERSION,
    SUPPORTED_BUILD_MODELS,
    DevelocityMCPServerConfig,
)
from requests import HTTPError, Response


class EnterpriseAPIService:
    def __init__(self, config: DevelocityMCPServerConfig, allow_untrusted_server: bool) -> None:
        self.url = config.server_url
        self.access_key = config.access_key
        self.verify_requests = not allow_untrusted_server

    def get_build_data_for_id(self, build_id: BuildId, build_models: BuildModels) -> list[dict[str, Any]]:
        api_url = f"{self.url}/api/builds/{build_id}"
        query_params = []

        # add build model params
        if not build_models.is_empty():
            query_params += build_models.to_params()

        return self._compress_builds_api_response(self._request(api_url, query_params).json())

    def get_build_data(
        self,
        advanced_query: AdvancedSearchQuery,
        build_models: BuildModels,
        max_builds: int = 100,
        from_build: str = None,
    ) -> list[dict[str, Any]]:
        api_url = f"{self.url}/api/builds"
        query_params = [("reverse", "true"), ("maxBuilds", max_builds)]

        # add build model params
        if not build_models.is_empty():
            query_params += build_models.to_params()

        # add advanced search query params
        if not advanced_query.is_empty():
            query_params.append(("query", advanced_query.to_param_string()))

        if from_build:
            query_params.append(("fromBuild", from_build))

        return self._compress_builds_api_response(self._request(api_url, query_params).json())

    def get_test_data(
        self,
        advanced_query: AdvancedSearchQuery,
        container: TestContainer = None,
        include_successful: IncludeSuccessfulTestsOption = False,
        include_failed: IncludeFailedTestsOption = False,
        include_skipped: IncludeSkippedTestsOption = False,
        include_flaky: IncludeFlakyTestsOption = False,
        include_not_selected: IncludePTSNotSelectedTestsOption = False,
    ) -> list[dict[str, Any]]:
        api_url = f"{self.url}/api/tests/containers"
        query_params = []
        if container is not None:
            query_params.append(("container", container))
        if include_successful:
            query_params.append(("testOutcomes", "successful"))
        if include_failed:
            query_params.append(("testOutcomes", "failed"))
        if include_skipped:
            query_params.append(("testOutcomes", "skipped"))
        if include_flaky:
            query_params.append(("testOutcomes", "flaky"))
        if include_not_selected:
            query_params.append(("testOutcomes", "notSelected"))

        query_params.append(("query", advanced_query.to_param_string()))
        return self._request(api_url, query_params).json()

    def get_raw_build_event_data(self, build_id: BuildId, event_type_name: str) -> dict[str, Any]:
        api_url = f"{self.url}/build-export/v2/build/{build_id}/events"
        params = [("eventTypes", event_type_name)]
        resp = self._request(api_url, params)
        return resp.text

    def _request(self, url: str, query_parms: list[tuple] = None) -> Response:
        headers = {"Authorization": f"Bearer {self.access_key}", "Accept": "application/json"}
        try:
            resp = requests.get(url, headers=headers, params=query_parms, timeout=60, verify=self.verify_requests)
            if resp.status_code != 200:
                raise HTTPError(
                    f"Error sending request to {url}: {resp.status_code} - {resp.text}. Parameters: {query_parms}"
                )
            return resp
        except HTTPError as e:
            raise e
        except Exception:
            raise HTTPError(f"Error sending request to Develocity API.")

    @staticmethod
    def _filter_unavailable_build_models_from_response(models: dict[str, Any]) -> dict[str, Any]:
        filtered_models = dict()
        for model_name, model_obj in models.items():
            if "problem" not in model_obj:
                filtered_models[model_name] = model_obj["model"]
        return filtered_models

    def _compress_builds_api_response(self, response: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(response, list):
            response = [response]
        compressed_response = []
        for build in response:
            if "models" in build:
                build["models"] = self._filter_unavailable_build_models_from_response(build["models"])
            compressed_response.append(build)
        return compressed_response
