# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Custom search command structure and standards

Custom search commands are defined in a **commands.conf** file in the **/default** directory of the app. For more, see [About writing custom search commands](https://docs.splunk.com/Documentation/Splunk/latest/Search/Aboutcustomsearchcommands) and [commands.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Commandsconf).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import PYTHON_3_VERSIONS, PYTHON_LATEST_VERSION, Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.custom_commands import Command
    from splunk_appinspect.reporter import Reporter


report_display_order = 20
logger = logging.getLogger(__name__)


class CheckCommandScriptsPythonVersion(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_command_scripts_python_version",
                description="Check that commands.conf must explicitly define the python.version "
                f"to be one of: {', '.join(PYTHON_3_VERSIONS)} as required for each python-scripted custom command.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
                depends_on_config=("commands",),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        custom_commands_conf = config["commands"]
        for command in custom_commands_conf.sections():
            file_path = custom_commands_conf.get_relative_path()
            command_file = command.get_option("filename") if command.has_option("filename") else None
            if not command_file:
                continue
            command_chunked = command.get_option("chunked") if command.has_option("chunked") else None
            if command_chunked:
                command_chunked = command_chunked.value
            python_version = command.get_option("python.version") if command.has_option("python.version") else None
            if python_version:
                python_version = python_version.value

            if (not command_chunked or command_chunked == "false") and command_file.value.endswith(".py"):
                if not python_version:
                    yield FailMessage(
                        f"Custom command {command.name} doesn't define python.version, "
                        f"python.version should be explicitly set to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                        file_path,
                    )
                elif python_version != PYTHON_LATEST_VERSION and python_version not in PYTHON_3_VERSIONS:
                    yield FailMessage(
                        f"Custom command {command.name} must define python.version to one of: {', '.join(PYTHON_3_VERSIONS)} values as required.",
                        file_name=file_path,
                        line_number=command["python.version"].lineno,
                    )
                elif python_version == PYTHON_LATEST_VERSION:
                    yield WarningMessage(
                        f"Custom command {command.name} specifies {PYTHON_LATEST_VERSION} for python.version. "
                        f"Note that python.version={PYTHON_LATEST_VERSION} is not supported for Splunk <= 9.2.",
                        file_name=file_path,
                        line_number=command["python.version"].lineno,
                    )
