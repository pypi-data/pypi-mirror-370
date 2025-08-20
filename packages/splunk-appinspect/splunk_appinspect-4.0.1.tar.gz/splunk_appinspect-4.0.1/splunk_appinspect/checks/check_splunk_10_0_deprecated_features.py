# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 10.0.0

The following features should not be supported in Splunk 10.0.0 or later. For more, see [Deprecated features](https://docs.splunk.com/Documentation/Splunk/10.0.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](https://docs.splunk.com/Documentation/Splunk/10.0.0/Installation/ChangesforSplunkappdevelopers).
"""

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.configuration_file import ConfigurationProxy
from splunk_appinspect.constants import BUILT_IN_ALERT_ACTIONS, Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.checks import CheckMessage
    from splunk_appinspect.custom_types import ConfigurationProxyType

logger = logging.getLogger(__name__)


class CheckOutdatedSSLTLS(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_outdated_ssl_tls",
                description="Connections using ssl3, tls1.0, tls1.1 are deprecated since Splunk 10.0 due to "
                "the OpenSSL dependency being updated to 3.0. Only valid TSL/SSL version is tls1.2.",
                depends_on_config=CheckOutdatedSSLTLS.CONFIGS_TO_CHECK,
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    CONFIGS_TO_CHECK = [
        "alert_actions",
        "authentication",
        "indexes",
        "inputs",
        "outputs",
        "savedsearches",
        "server",
        "web",
    ]

    SSL_OPTION_NAMES = ["sslVersions", "sslVersionsForClient"]
    SSL_OPTION_PATTERNS = [".sslVersions", ".sslVersionsForClient"]

    def check_config(
        self,
        app: splunk_appinspect.App,
        config: "ConfigurationProxyType",
    ) -> Generator["CheckMessage", Any, None]:
        for config_name in self.CONFIGS_TO_CHECK:
            config_file = config[config_name]
            if not config_file:
                continue
            for section in config_file.sections():
                for option in section.options.values():
                    if option.name in self.SSL_OPTION_NAMES or any(
                        option.name.endswith(pattern) for pattern in self.SSL_OPTION_PATTERNS
                    ):
                        yield FailMessage(
                            "The Splunk platform supports TLS 1.2 as default. Please ensure your app’s configuration "
                            "is indicating TLS 1.2 only - TLS 1.0, TLS 1.1 are deprecated and SSL 3, "
                            "TLS 1.3 are not supported.",
                            file_name=option.get_relative_path(),
                            line_number=option.get_line_number(),
                        )


class CheckInvokingBundledNode(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_invoking_bundled_node",
                description="Check that there are no invocations of a Splunk NodeJS binary in any of the app files.",
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

    def check(self, app: "App") -> Generator["CheckMessage", Any, None]:
        patterns = [r"cmd node", r"(\"|\')cmd(\"|\')\, ?(\"|\')node(\"|\')"]

        matches = app.search_for_patterns(
            patterns=patterns,
            excluded_types=[".txt", ".md", ".org", ".rst"],
        )
        if not matches:
            yield NotApplicableMessage("No invocations of bundled NodeJS binary found.")
            return

        for fileref_output, match in matches:
            filepath, line_number = fileref_output.split(":")
            yield WarningMessage(
                f"The command `{match.group()}`, which invokes a bundled NodeJS binary, was found. "
                "As of Splunk Enterprise 10.0, Node.js is deprecated and will be removed in a future release.",
                file_name=filepath,
                line_number=line_number,
            )


class CheckForJsInSavedSearchesActionScript(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_js_in_saved_searches_action_script",
                description="Check that savedsearch.conf stanzas do not set action.script.filename to a JS script.",
                depends_on_config=("savedsearches",),
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

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator["CheckMessage", Any, None]:
        for section in config["savedsearches"].sections():
            if section.has_option("action.script.filename"):
                action_option = section.get_option("action.script.filename")
                if action_option.value.endswith(".js"):
                    yield WarningMessage(
                        f"The saved search [{section.name}] contains action.script.filename, which points to a JS script. "
                        "As of Splunk Enterprise 10.0, Node.js is deprecated and will be removed in a future release.",
                        file_name=action_option.get_relative_path(),
                        line_number=action_option.get_line_number(),
                    )


class CheckJsCustomAlertActions(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_js_custom_alert_actions",
                description="Check that each custom alert action is not calling a JS script, which requires a Splunk NodeJS Binary.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                    Tags.FUTURE,
                ),
                depends_on_config=("alert_actions",),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator["CheckMessage", Any, None]:

        for alert_action in config["alert_actions"].sections():
            if alert_action.name in BUILT_IN_ALERT_ACTIONS:
                # Not a custom alert action
                continue
            if not alert_action.has_option("alert.execute.cmd"):
                continue
            alert_execute_cmd = alert_action.get_option("alert.execute.cmd")
            if alert_execute_cmd.value.endswith(".js"):
                yield WarningMessage(
                    f"The alert action: `{alert_action.name}` specifies a script which is a JavaScript script. "
                    "As of Splunk Enterprise 10.0, Node.js is deprecated and will be removed in a future release.",
                    file_name=alert_execute_cmd.get_relative_path(),
                    line_number=alert_execute_cmd.get_line_number(),
                )


class CheckJsUseInModularInputs(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_js_use_in_modular_inputs",
                description="Check that there are no modular inputs invoking a JS script.",
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

    @Check.depends_on_files(
        basedir=["README"],
        names=["inputs.conf.spec"],
        recurse_depth=0,
        not_applicable_message="No `inputs.conf.spec` file exists.",
    )
    def check_inputs_conf_spec(self, app: "App", path_in_app: Path) -> Generator["CheckMessage", Any, None]:
        modular_inputs = app.get_modular_inputs()

        if modular_inputs.has_modular_inputs():
            file_path = Path("README", "inputs.conf.spec")
            for mi in modular_inputs.get_modular_inputs():
                # Modular inputs could point to js files, even without including the extension
                # Look for any associated js scripts in the standard bin folders
                for p in app.base_bin_dirs:
                    test_path = app.get_filename(p, mi.name + ".js")
                    if test_path.exists():
                        yield WarningMessage(
                            f"The modular input: `{mi.name}` points to a JavaScript script. "
                            "As of Splunk Enterprise 10.0, Node.js is deprecated and will be removed in a future release.",
                            file_name=file_path,
                            line_number=mi.lineno,
                        )


class CheckJsUseInScriptedInputs(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_js_use_in_scripted_inputs",
                description="Check that there are no scripted inputs invoking a JS script.",
                depends_on_config=("inputs",),
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.FUTURE,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator["CheckMessage", Any, None]:
        scripted_inputs_cmd_path_pattern = "script://(.*)$"
        with_path_suffix_pattern = r".*\.js$"

        inputs_conf = config["inputs"]
        for section in inputs_conf.sections():
            # find cmd path of [script://xxx] stanzas in inputs.conf
            path = re.findall(scripted_inputs_cmd_path_pattern, section.name)
            if path:
                path = path[0]
                if re.match(with_path_suffix_pattern, path):
                    yield WarningMessage(
                        f"The scripted input [{section.name}] calls a JavaScript script. "
                        "As of Splunk Enterprise 10.0, Node.js is deprecated and will be removed in a future release.",
                        file_name=section.get_relative_path(),
                        line_number=section.lineno,
                    )
