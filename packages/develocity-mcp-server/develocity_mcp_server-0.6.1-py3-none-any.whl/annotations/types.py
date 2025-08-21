from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import Field

ATTRIBUTES_BUILD_MODELS = [
    "gradle-attributes",
    "maven-attributes",
    "bazel-attributes",
    "python-attributes",
    "npm-attributes",
]
DEPENDENCY_BUILD_MODELS = ["gradle-dependencies", "maven-dependencies", "maven-dependency-resolution"]
RESOURCE_USAGE_BUILD_MODELS = [
    "gradle-resource-usage",
    "maven-resource-usage",
    "gradle-build-profile-overview",
    "maven-build-profile-overview",
    "gradle-network-activity",
]
TEST_PERFORMANCE_BUILD_MODELS = ["gradle-test-performance", "maven-test-performance"]

BuildId = Annotated[
    str,
    Field(
        description="Unique id of the Develocity build scan. When present, results are returned only for this build.",
        min_length=13,
        max_length=13,
    ),
]
MinDatetime = Annotated[
    datetime, Field(description="If set, no results that from before this datetime will be returned.")
]
MaxDatetime = Annotated[
    datetime, Field(description="If set, no results that from after this datetime will be returned.")
]
User = Annotated[
    str,
    Field(
        description="Username of the account that executed the build. If a user asks about 'my builds' or 'builds run by me', you should ask them what their Develocity username is and use it here to filter results",
        min_length=1,
    ),
]
HostName = Annotated[str, Field(description="Public hostname of the machine that executed the build.", min_length=1)]
Project = Annotated[
    str,
    Field(
        description="Name of the Gradle root project, Maven top level module, Bazel workspace, or sbt root project.",
        min_length=1,
    ),
]
RequestedTarget = Annotated[
    str, Field(description="Tasks/goals/targets that were requested when the build was started.", min_length=1)
]
BuildTool = Literal["gradle", "maven", "bazel", "sbt", "npm", "python"]
UserTags = Annotated[
    list[str],
    Field(
        description="""List of strings which match custom metadata tags added to build scans by the user. Common tags include...
    - 'LOCAL' for locally executed builds
    - 'CI' for builds executed on a remote CI server
    - 'DIRTY' for builds executed with a working directory that has had modifications
    - The value of the git branch the build was executed with""",
        min_length=1,
    ),
]
BuildOutcome = Literal["succeeded", "failed"]
IncludeAttributesOption = Annotated[
    bool,
    Field(
        description="""If True, returns additional metadata about the returned builds. This includes the following...
    - build start time and duration
    - project name
    - requested tasks/goals/targets
    - build outcome, e.g., passed or failed
    - tags (user-defined list of simple strings)
    - custom values (user-defined list of key-value pairs)
    - Develocity-specific settings and build tool-specific settings
    - details about the environment where the build was run"""
    ),
]
IncludeDependenciesOption = Annotated[
    bool, Field(description="If True, returns information about the returned builds' dependencies.")
]
IncludeBuildPerformanceOption = Annotated[
    bool,
    Field(
        description="If True, returns a detailed breakdown of build task/goal/target execution times, resource usage metrics, dependency resolution times, and dependency resolution times for the returned builds."
    ),
]
IncludeTestPerformanceOption = Annotated[
    bool, Field(description="If True, returns test performance metrics for the returned builds.")
]
MaxBuilds = Annotated[
    int,
    Field(description="limits the maximum number of builds to return in a single request.", gt=0, le=1000, default=100),
]

TestContainer = Annotated[
    str,
    Field(
        description="Name of the test container. Allows restricting the search to parts of the test container hierarchy. "
        "Wildcards can be used to match an entire package. Example: com.example.* will return results for all test containers in the com.example package.",
        min_length=1,
    ),
]
IncludeSuccessfulTestsOption = Annotated[bool, Field(description="If True, includes results for successful tests.")]
IncludeFailedTestsOption = Annotated[bool, Field(description="If True, includes results for failed tests.")]
IncludeSkippedTestsOption = Annotated[bool, Field(description="If True, includes results for skipped tests.")]
IncludeFlakyTestsOption = Annotated[bool, Field(description="If True, includes results for flaky tests.")]
IncludePTSNotSelectedTestsOption = Annotated[
    bool,
    Field(
        description="If True, includes results for tests that were not selected by Develocity Predictive Test Selection (PTS)."
    ),
]


class AdvancedSearchQuery:
    def __init__(
        self,
        min_datetime: MinDatetime,
        max_datetime: MaxDatetime,
        user: User,
        hostname: HostName,
        project: Project,
        requested_target: RequestedTarget,
        build_tool: BuildTool,
        tags: UserTags,
        build_outcome: BuildOutcome,
    ):
        self.min_datetime = self._format_datetime(min_datetime) if min_datetime is not None else None
        self.max_datetime = self._format_datetime(max_datetime) if max_datetime is not None else None
        self.user = user
        self.hostname = hostname
        self.project = project
        self.requested_target = requested_target
        self.build_tool = build_tool
        self.tags = tags
        self.build_outcome = build_outcome

    def is_empty(self) -> bool:
        return (
            self.user is None
            and self.hostname is None
            and self.project is None
            and self.requested_target is None
            and self.build_tool is None
            and self.tags is None
            and self.build_outcome is None
            and self.min_datetime is None
            and self.max_datetime is None
        )

    def _format_datetime(self, dt: datetime) -> str:
        dt = dt.replace(tzinfo=None)
        return dt.isoformat(timespec="seconds")

    def to_param_string(self) -> str:
        query_parts = []
        if self.user:
            query_parts.append(f"user:{self.user}")
        if self.hostname:
            query_parts.append(f"hostname:{self.hostname}")
        if self.project:
            query_parts.append(f"project:{self.project}")
        if self.requested_target:
            query_parts.append(f"requested:{self.requested_target}")
        if self.build_tool:
            query_parts.append(f"buildTool:{self.build_tool}")
        if self.tags:
            query_parts.append(f"tag:{','.join(self.tags)}")
        if self.build_outcome:
            query_parts.append(f"buildOutcome:{'failed' if self.build_outcome else 'succeeded'}")
        if self.min_datetime or self.max_datetime:
            min_dt = (
                self.min_datetime
                if self.min_datetime is not None
                else self._format_datetime(datetime.fromtimestamp(0, timezone.utc))
            )
            max_dt = self.max_datetime if self.max_datetime is not None else self._format_datetime(datetime.now())
            query_parts.append(f"buildStartTime:[{min_dt} to {max_dt}]")
        return " and ".join(query_parts)


class BuildModels:
    def __init__(
        self,
        include_attributes: IncludeAttributesOption,
        include_dependencies: IncludeDependenciesOption,
        include_build_performance: IncludeBuildPerformanceOption,
        include_test_performance: IncludeTestPerformanceOption,
    ):
        self.build_models = []
        if include_attributes:
            self.build_models += ATTRIBUTES_BUILD_MODELS
        if include_dependencies:
            self.build_models += DEPENDENCY_BUILD_MODELS
        if include_build_performance:
            self.build_models += RESOURCE_USAGE_BUILD_MODELS
        if include_test_performance:
            self.build_models += TEST_PERFORMANCE_BUILD_MODELS

    def is_empty(self) -> bool:
        return len(self.build_models) == 0

    def to_params(self) -> list[tuple[str, str]]:
        return [("models", m) for m in self.build_models]
