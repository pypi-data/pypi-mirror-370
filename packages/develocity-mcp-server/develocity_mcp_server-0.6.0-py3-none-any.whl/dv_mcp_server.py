import argparse
import os
from typing import Any

import requests
from annotations.types import (
    ATTRIBUTES_BUILD_MODELS,
    DEPENDENCY_BUILD_MODELS,
    RESOURCE_USAGE_BUILD_MODELS,
    TEST_PERFORMANCE_BUILD_MODELS,
    AdvancedSearchQuery,
    BuildId,
    BuildModels,
    BuildOutcome,
    BuildTool,
    HostName,
    IncludeAttributesOption,
    IncludeBuildPerformanceOption,
    IncludeDependenciesOption,
    IncludeFailedTestsOption,
    IncludeFlakyTestsOption,
    IncludePTSNotSelectedTestsOption,
    IncludeSkippedTestsOption,
    IncludeSuccessfulTestsOption,
    IncludeTestPerformanceOption,
    MaxBuilds,
    MaxDatetime,
    MinDatetime,
    Project,
    RequestedTarget,
    TestContainer,
    User,
    UserTags,
)
from config import DevelocityMCPServerConfig
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from services.dv_api import EnterpriseAPIService


def _get_allow_untrusted_server_flag() -> bool:
    raw_val = os.getenv("DEVELOCITY_MCP_ALLOW_UNTRUSTED_SERVER")
    return raw_val is not None and raw_val.lower() == "true"


mcp = FastMCP("Develocity MCP", mask_error_details=True)
print(_get_allow_untrusted_server_flag())
config = DevelocityMCPServerConfig(_get_allow_untrusted_server_flag())
api_service = EnterpriseAPIService(config, _get_allow_untrusted_server_flag())

# Adjust available tools based on DV version
supported_build_models = set(config.dv_version.get_supported_build_models())
excluded_builds_tool_options = []
ATTRIBUTES_BUILD_MODELS = [m for m in ATTRIBUTES_BUILD_MODELS if m in supported_build_models]
DEPENDENCY_BUILD_MODELS = [m for m in DEPENDENCY_BUILD_MODELS if m in supported_build_models]
if len(DEPENDENCY_BUILD_MODELS) == 0:
    excluded_builds_tool_options.append("include_dependencies")
RESOURCE_USAGE_BUILD_MODELS = [m for m in RESOURCE_USAGE_BUILD_MODELS if m in supported_build_models]
if len(RESOURCE_USAGE_BUILD_MODELS) == 0:
    excluded_builds_tool_options.append("include_build_performance")
TEST_PERFORMANCE_BUILD_MODELS = [m for m in TEST_PERFORMANCE_BUILD_MODELS if m in supported_build_models]
if len(TEST_PERFORMANCE_BUILD_MODELS) == 0:
    excluded_builds_tool_options.append("include_test_performance")


@mcp.tool(name="get-develocity-build-data", exclude_args=excluded_builds_tool_options)
def get_builds(
    build_id: BuildId = None,
    min_datetime: MinDatetime = None,
    max_datetime: MaxDatetime = None,
    user: User = None,
    hostname: HostName = None,
    project: Project = None,
    requested_target: RequestedTarget = None,
    build_tool: BuildTool = None,
    tags: UserTags = None,
    build_outcome: BuildOutcome = None,
    include_attributes: IncludeAttributesOption = None,
    include_dependencies: IncludeDependenciesOption = None,
    include_build_performance: IncludeBuildPerformanceOption = None,
    include_test_performance: IncludeTestPerformanceOption = None,
    max_builds: MaxBuilds = 100,
    from_build: str = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Returns builds scan information using the Develocity builds API. Results are always returned in reverse chronological order (newest to oldest).

    The tool does not return all results. If the number of results is equal to the value of the max_builds, consider using pagination.
    """
    query = AdvancedSearchQuery(
        min_datetime, max_datetime, user, hostname, project, requested_target, build_tool, tags, build_outcome
    )
    build_models = BuildModels(
        include_attributes, include_dependencies, include_build_performance, include_test_performance
    )
    if build_id is not None:
        return api_service.get_build_data_for_id(build_id, build_models)
    else:
        return api_service.get_build_data(query, build_models, max_builds, from_build)


@mcp.tool(name="get-develocity-test-results-data")
def get_test_results(
    min_datetime: MinDatetime = None,
    max_datetime: MaxDatetime = None,
    user: User = None,
    hostname: HostName = None,
    project: Project = None,
    requested_target: RequestedTarget = None,
    build_tool: BuildTool = None,
    tags: UserTags = None,
    build_outcome: BuildOutcome = None,
    container: TestContainer = "*",
    include_successful: IncludeSuccessfulTestsOption = False,
    include_failed: IncludeFailedTestsOption = False,
    include_skipped: IncludeSkippedTestsOption = False,
    include_flaky: IncludeFlakyTestsOption = False,
    include_not_selected: IncludePTSNotSelectedTestsOption = False,
) -> dict[str, Any]:
    """Returns the distribution of test outcomes for a given set of test containers or test cases, using the Develocity tests API."""
    if (
        include_successful == False
        and include_failed == False
        and include_skipped == False
        and include_flaky == False
        and include_not_selected == False
    ):
        raise ToolError(
            "You must include at least one type of test outcome. "
            "Of the following options at least one must be set to 'True': "
            "include_successful, include_failed, include_skipped, include_flaky, include_not_selected"
        )

    query = AdvancedSearchQuery(
        min_datetime, max_datetime, user, hostname, project, requested_target, build_tool, tags, build_outcome
    )
    if query.is_empty():
        raise ToolError(
            "At least one filtering option must be used when retrieving test data from Develocity. "
            "If you have none, try setting the min_datetime and max_datetime parameters to filter to a specific date range."
        )
    return api_service.get_test_data(
        query, container, include_successful, include_failed, include_skipped, include_flaky, include_not_selected
    )


@mcp.tool(name="get-failure-data-for-develocity-build")
def get_failure_data_for_build(build_id: BuildId):
    """Returns exception classes, exception messages, and stack trace information for a single Develocity build that failed."""
    return api_service.get_raw_build_event_data(build_id, "ExceptionData")


@mcp.tool(name="get-configured_repositories-for-develocity-build")
def get_configured_repositories_for_build(build_id: BuildId):
    """Returns configured repositories (e.g. Maven repositories) for a single Develocity build."""
    return api_service.get_raw_build_event_data(build_id, "Repository")


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
