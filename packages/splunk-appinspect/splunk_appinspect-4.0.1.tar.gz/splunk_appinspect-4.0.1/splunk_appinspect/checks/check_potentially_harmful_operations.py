# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Operating system standards
"""
import logging
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.reporter import Reporter

from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.configuration_file import ConfigurationFile, ConfigurationSection

report_display_order = 5
logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_destructive_commands(app: "App", reporter: "Reporter") -> None:
    """Check for the use of malicious shell commands in configuration files or shell scripts to
    corrupt the OS or Splunk instance. Other scripting languages are covered by other checks."""
    # The second is to match process.call(["rm", "-rf"]) and friends
    exclude = [".txt", ".md", ".org", ".csv", ".rst", ".py", ".js"]
    patterns = ["rm -rf", r"""["']rm["']\s*,\s*["']\-[rf]{2}["']""", "kill\b", "halt\b"]
    matches = app.search_for_patterns(patterns, excluded_types=exclude)
    for fileref_output, match in matches:
        filepath, line_number = fileref_output.split(":")
        reporter_output = ("The prohibited command {} was found. File: {} Line: {}.").format(
            match.group(), filepath, line_number
        )
        reporter.fail(reporter_output, filepath, line_number)


class CheckRunShellScriptCommand(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_runshellscript_command",
                description="Check that `runshellscript` command is not used. This command is considered risky because, if used incorrectly, it can pose a security risk or potentially lose data when it runs.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
            )
        )

    def check(self, app: "App") -> Generator[CheckMessage, Any, None]:
        pattern = [r"\|\s*runshellscript"]

        matches = app.search_for_patterns(patterns=pattern)

        for fileref_output, match in matches:
            file_path, line_number = fileref_output.split(":")

            yield FailMessage(
                message="The prohibited command `runshellscript` was found.",
                file_name=file_path,
                line_number=line_number,
            )
