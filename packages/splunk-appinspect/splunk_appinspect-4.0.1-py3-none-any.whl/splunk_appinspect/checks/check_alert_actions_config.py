# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Alert actions structure and standards

Custom alert actions are defined in an **alert_actions.conf** file located in the **/default** directory of the app. For more, see [Custom alert actions overview](https://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModAlertsIntro) and [alert_actions.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Alertactionsconf).
"""
from __future__ import annotations

import logging
import os.path
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.app_util import is_manipulation_outside_of_app_container
from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import BUILT_IN_ALERT_ACTIONS, PYTHON_3_VERSIONS, PYTHON_LATEST_VERSION, Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.alert_actions import AlertAction
    from splunk_appinspect.custom_types import ConfigurationProxyType
    from splunk_appinspect.file_resource import FileResource
    from splunk_appinspect.reporter import Reporter


report_display_order = 20

logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.PRIVATE_CLASSIC,
    Tags.MIGRATION_VICTORIA,
)
def check_alert_actions_exe_exist(app: "App", reporter: "Reporter") -> None:
    """Check that each custom alert action has a valid executable. If it does, further check
    if the executable is Python script. If it does, further check it's Python 3 compatible."""

    # a) is there an overloaded cmd in the stanza e.g. execute.cmd
    # b) is there a file in default/bin for the files in nix_exes & windows_exes (one of each for platform-agnostic)
    # c) is there a file in a specific arch directory for all

    alert_actions = app.get_alert_actions()
    if alert_actions.has_configuration_file():
        filename = Path("default", "alert_actions.conf")
        for alert in alert_actions.get_alert_actions():
            if alert.name in BUILT_IN_ALERT_ACTIONS:
                # Not a custom alert action
                continue

            if alert.alert_execute_cmd_specified():
                # Highlander: There can be only one...
                if alert.executable_files[0].exists():
                    _check_python_version_in_alert_action(alert, alert.executable_files[0], reporter, filename)
                else:
                    lineno = alert.args["alert.execute.cmd"][1]
                    mess = (
                        f"No alert action executable for {alert.alert_execute_cmd} was found in the "
                        f"bin directory. File: {filename}, Line: {lineno}."
                    )
                    reporter.fail(mess, filename, lineno)
            elif "command" in alert.args:
                continue
            else:
                # The following logic will only take effect when running interpreter
                # in Python 3
                for file_resource in alert_actions.find_exes(alert.name):
                    _check_python_version_in_alert_action(alert, file_resource, reporter, filename)

                # a) is there a cross plat file (.py, .js) in default/bin?
                if alert.count_cross_plat_exes() > 0:
                    continue

                # b) is there a file per plat in default/bin?
                if alert.count_linux_exes() > 0:
                    continue

                reporter_output = f"No executable was found for alert action {alert.name}."
                reporter.fail(reporter_output, filename, alert.lineno)

    else:
        reporter_output = "No `alert_actions.conf` was detected."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
)
def check_for_payload_format(app: "App", reporter: "Reporter") -> None:
    """Check that each custom alert action's payload format has a value of `xml`
    or `json`.
    """
    alert_actions = app.get_alert_actions()
    if alert_actions.has_configuration_file():
        filename = Path("default", "alert_actions.conf")
        for alert in alert_actions.get_alert_actions():
            for arg in alert.args:
                if arg == "payload_format":
                    if not alert.args["payload_format"][0] == "json" and not alert.args["payload_format"][0] == "xml":
                        lineno = alert.args["payload_format"][1]
                        reporter_output = (
                            "The alert action must specify"
                            " either 'json' or 'xml' as the"
                            f" payload. File: {filename}, Line: {lineno}."
                        )
                        reporter.fail(reporter_output, filename, lineno)


class CheckForExplicitExeArgs(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_explicit_exe_args",
                description="Check whether any custom alert actions have executable arguments.",
                tags=[
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                ],
                depends_on_config=("alert_actions",),
            ),
        )

    def check_config(
        self,
        app: splunk_appinspect.App,
        config: "ConfigurationProxyType",
    ) -> Generator["CheckMessage", Any, None]:
        filename = Path("default", "alert_actions.conf")
        app_name = app.name
        for alert in app.get_alert_actions().get_alert_actions():
            for arg in alert.args:
                arg_value, lineno = alert.args[arg]
                if "alert.execute.cmd.arg" not in arg or not _is_possible_path(arg_value):
                    continue

                path = app.get_filename("bin", arg_value[arg_value.rfind(os.path.sep) + 1 :])

                if is_manipulation_outside_of_app_container(arg_value, app_name):
                    yield FailMessage(
                        "The alert action specifies executable arguments which is a file outside of the app directory "
                        f" {arg}: {arg_value}, which is not allowed.",
                        file_name=filename,
                        line_number=lineno,
                    )
                elif not path.exists():
                    yield FailMessage(
                        f"Path specified in alert.execute.cmd.arg does not exist {arg}: {arg_value}.",
                        file_name=filename,
                        line_number=lineno,
                    )


class CheckForExplicitExeArgsPrivate(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_explicit_exe_args_private",
                description="Check whether any custom alert actions have executable arguments.",
                tags=[
                    Tags.SPLUNK_APPINSPECT,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ],
                depends_on_config=("alert_actions",),
            ),
        )

    def check_config(
        self,
        app: splunk_appinspect.App,
        config: "ConfigurationProxyType",
    ) -> Generator["CheckMessage", Any, None]:
        filename = Path("default", "alert_actions.conf")
        app_name = app.name
        for alert in app.get_alert_actions().get_alert_actions():
            for arg in alert.args:
                arg_value, lineno = alert.args[arg]
                if "alert.execute.cmd.arg" not in arg or not _is_possible_path(arg_value):
                    continue

                path = app.get_filename("bin", arg_value[arg_value.rfind(os.path.sep) + 1 :])

                if is_manipulation_outside_of_app_container(arg_value, app_name):
                    yield WarningMessage(
                        "The alert action specifies executable arguments which is a file outside of the app directory "
                        f" {arg}: {arg_value}, which is not allowed.",
                        file_name=filename,
                        line_number=lineno,
                    )
                elif not path.exists():
                    yield WarningMessage(
                        f"Path specified in alert.execute.cmd.arg does not exist {arg}: {arg_value}.",
                        file_name=filename,
                        line_number=lineno,
                    )


def _is_possible_path(parameter: str) -> bool:
    return not parameter.startswith("-") and os.path.sep in parameter


def _check_python_version_in_alert_action(
    alert: "AlertAction", file_resource: "FileResource", reporter: "Reporter", config_file_path: Path
) -> None:
    if file_resource.file_path.name.endswith("py"):
        if alert.python_version != PYTHON_LATEST_VERSION and alert.python_version not in PYTHON_3_VERSIONS:
            reporter_output = (
                f" The `alert_actions.conf` stanza [{alert.name}] is using python script as alert script"
                f" but not specifying python.version to one of: {', '.join(PYTHON_3_VERSIONS)} as required."
            )
            reporter.fail(reporter_output, config_file_path)
        elif alert.python_version == PYTHON_LATEST_VERSION:
            reporter_output = (
                f" The `alert_actions.conf` stanza [{alert.name}] is using python script as alert script"
                f" that specifies python.version={PYTHON_LATEST_VERSION}."
                f" Note that python.version={PYTHON_LATEST_VERSION} is not supported for Splunk <= 9.2."
            )
            reporter.warn(reporter_output, config_file_path)
    else:
        # Do nothing because it's not Python script
        pass
