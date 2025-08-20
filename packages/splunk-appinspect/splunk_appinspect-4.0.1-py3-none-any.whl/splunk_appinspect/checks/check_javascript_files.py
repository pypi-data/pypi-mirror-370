# Copyright 2019 Splunk Inc. All rights reserved.

"""
### JavaScript file standards
"""

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any as AnyType
from typing import Generator, Tuple

import lxml.etree as et
import semver

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.regex_matcher import (
    ConfEndpointMatcher,
    JSTelemetryEndpointMatcher,
    JSTelemetryMetricsMatcher,
    JSWeakEncryptionMatcher,
)
from splunk_appinspect.telemetry_configuration_file import TelemetryConfigurationFile

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.reporter import Reporter
    from splunk_appinspect.validation_report import ApplicationValidationReport


logger = logging.getLogger(__name__)


class CheckJavaScriptSdkVersion(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_javascript_sdk_version",
                description="Check that Splunk SDK for JavaScript is up-to-date.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                    Tags.FUTURE,
                ),
            )
        )

    MINIMUM_SDK_VERSION = semver.VersionInfo.parse("2.0.0")
    LATEST_SDK_VERSION = semver.VersionInfo.parse("2.0.2")

    VERSION_PATTERN = r"\"version\"\s*:\s*\"(.*?)\""

    def check(self, app: "App") -> Generator[CheckMessage, AnyType, None]:
        # Parse the found version into semver, correcting for
        # bad versions like "0.1" without a patch version

        raw_version = None
        path_in_app = ""
        line_number = None
        parsed_ver = None
        try:
            for dirname, filename, _ in app.iterate_files(basedir=["appserver", "lib", "bin"]):
                if "splunk-sdk-javascript" in str(dirname) and filename == "package.json":
                    path_in_app = Path(dirname, filename)
                    line_number, raw_version, path_in_app = self._get_sdk_version(app, path_in_app.parent)

                    if len(raw_version.split(".")) == 2:
                        raw_version += ".0"  # correct for versions without a patch
                    parsed_ver = semver.VersionInfo.parse(raw_version)

        except Exception as err:
            yield WarningMessage(
                f"Issue parsing version found for the Splunk SDK for JavaScript ({raw_version}). Error: {err}.",
                file_name=path_in_app,
                line_number=line_number,
            )
            return

        if parsed_ver is None:
            yield NotApplicableMessage("Splunk SDK for JavaScript not found.")
            return

        if parsed_ver < self.MINIMUM_SDK_VERSION:
            yield WarningMessage(
                f"Detected an outdated version of the Splunk SDK for JavaScript ({raw_version}).",
                file_name=path_in_app,
                line_number=line_number,
                remediation=f"Upgrade to {self.MINIMUM_SDK_VERSION} or later.",
            )
        elif self.MINIMUM_SDK_VERSION <= parsed_ver < self.LATEST_SDK_VERSION:
            yield NotApplicableMessage(
                f"Detected an outdated version of the Splunk SDK for JavaScript ({raw_version}).",
                file_name=path_in_app,
                line_number=line_number,
                remediation=f"Upgrade to {self.LATEST_SDK_VERSION} or later.",
            )
        else:
            yield NotApplicableMessage(
                f"Splunk SDK for JavaScript detected (version {raw_version}).",
                file_name=path_in_app,
                line_number=line_number,
                remediation="No action required at this time.",
            )

    @staticmethod
    def _decode_result(result):
        file_path, match = result[0]
        line_number = file_path.split(":")[1]
        version_raw = match.groups()[0]
        return line_number, version_raw

    def _get_sdk_version(self, app: "App", base_dir: Path) -> Tuple:
        """
        Check package.json file in splunk-sdk-javascript dir
        """
        version_file = "package.json"

        result = app.search_for_patterns([self.VERSION_PATTERN], basedir=base_dir, names=[version_file])
        line_number, version_raw = self._decode_result(result)

        file_path = base_dir.joinpath(version_file)

        return line_number, version_raw, file_path


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_telemetry_endpoint_usage_in_javascript(app: "App", reporter: "Reporter") -> None:
    """Check that app does not use REST endpoint to collect and send telemetry data."""

    telemetry_config = TelemetryConfigurationFile()
    if not telemetry_config.check_allow_list(app):
        matcher = JSTelemetryEndpointMatcher()

        # also covered the python file search in this check
        # for simplicity, does not separate this part to check_python_files.py
        for result, file_path, lineno in matcher.match_results_iterator(
            app.app_dir, app.iterate_files(types=[".js", ".py"])
        ):
            reporter.fail(
                "The telemetry-metric REST endpoint usage is prohibited in order to protect from "
                "sending sensitive information. Consider using logging. "
                "See: https://dev.splunk.com/enterprise/docs/developapps/addsupport/logging/loggingsplunkextensions/."
                f" Match: {result}",
                file_path,
                lineno,
            )

        if not matcher.has_valid_files:
            reporter_output = "No JavaScript files found."
            reporter.not_applicable(reporter_output)

    else:
        # This app is authorized for telemetry check. Pass it.
        pass


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_telemetry_metrics_in_javascript(app: "App", reporter: "Reporter") -> None:
    """Check for usages of telemetry metrics in JavaScript"""

    telemetry_config = TelemetryConfigurationFile()
    if not telemetry_config.check_allow_list(app):
        matcher = JSTelemetryMetricsMatcher()
        for result, file_path, lineno in matcher.match_results_iterator(app.app_dir, app.iterate_files(types=[".js"])):
            reporter_output = (
                "The telemetry operations are not permitted in order to protect from sending sensitive information. "
                "Consider using logging. "
                "See: https://dev.splunk.com/enterprise/docs/developapps/addsupport/logging/loggingsplunkextensions/."
                f" Match: {result}"
            )
            reporter.fail(reporter_output, file_path, lineno)

        if not matcher.has_valid_files:
            reporter_output = "No JavaScript files found."
            reporter.not_applicable(reporter_output)

    else:
        # This app is authorized for telemetry check. Pass it.
        pass
