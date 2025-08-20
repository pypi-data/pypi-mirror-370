# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Modular inputs structure and standards

Modular inputs are configured in an **inputs.conf.spec** file located in the **/README** directory of the app. For more, see [Modular inputs overview](https://dev.splunk.com/enterprise/docs/developapps/manageknowledge/custominputs/), [Modular inputs configuration](https://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsSpec), and [Modular inputs basic example](https://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsBasicExample#Basic_implementation_requirements).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import PYTHON_3_VERSIONS, PYTHON_LATEST_VERSION, Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.reporter import Reporter


report_display_order = 12

logger = logging.getLogger(__name__)


class CheckInputsConfSpecStanzasHasPythonVersionProperty(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_inputs_conf_spec_stanzas_has_python_version_property",
                description="Check that all the modular inputs defined in inputs.conf.spec explicitly"
                f" set the python.version to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                depends_on_config=("inputs",),
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

    @Check.depends_on_files(
        basedir=["README"],
        names=["inputs.conf.spec"],
        recurse_depth=0,
        not_applicable_message="No `inputs.conf.spec` file exists.",
    )
    def check_inputs_conf_spec(self, app: "App", path_in_app: Path) -> Generator[CheckMessage, Any, None]:
        modular_inputs = app.get_modular_inputs()

        if not modular_inputs.has_modular_inputs():
            yield NotApplicableMessage("No modular inputs were detected.")
            return

        for config in (app.default_config, app.merged_config, *app.user_merged_config.values()):
            yield from self.check_inputs_config(app, config) or []

    def check_inputs_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        modular_inputs = app.get_modular_inputs()

        inputs_config = config["inputs"]

        global_default_python = None
        if inputs_config and inputs_config.has_option("default", "python.version"):
            global_default_python = inputs_config.get_option("default", "python.version")

        for modular_input in modular_inputs.get_modular_inputs():
            if modular_input.count_cross_plat_exes() == 0:
                continue

            input_python_version = None
            if inputs_config and inputs_config.has_option(modular_input.name, "python.version"):
                input_python_version = inputs_config.get_option(modular_input.name, "python.version")

            if input_python_version is not None:
                if (
                    input_python_version.value != PYTHON_LATEST_VERSION
                    and input_python_version.value not in PYTHON_3_VERSIONS
                ):
                    yield FailMessage(
                        f"Modular input `{modular_input.name}` specifies `{input_python_version.value}` "
                        f"for `python.version`, which should be set to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                        file_name=input_python_version.get_relative_path(),
                        line_number=input_python_version.get_line_number(),
                    )
                elif input_python_version.value == PYTHON_LATEST_VERSION:
                    yield WarningMessage(
                        f"Modular input `{modular_input.name}` specifies `{PYTHON_LATEST_VERSION}` "
                        f"for `python.version`. "
                        f"Note that python.version={PYTHON_LATEST_VERSION} is not supported for Splunk <= 9.2.",
                        file_name=input_python_version.get_relative_path(),
                        line_number=input_python_version.get_line_number(),
                    )
            elif global_default_python is not None:
                if (
                    global_default_python.value != PYTHON_LATEST_VERSION
                    and global_default_python.value not in PYTHON_3_VERSIONS
                ):
                    yield FailMessage(
                        f"Modular input `{modular_input.name} does not specify a `python.version`, and "
                        f"the `[default]` stanza in {global_default_python.get_relative_path()} "
                        f"specifies {global_default_python.value}, "
                        f"which should be set to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                        file_name=global_default_python.get_relative_path(),
                        line_number=global_default_python.get_line_number(),
                    )
                elif global_default_python.value == PYTHON_LATEST_VERSION:
                    yield WarningMessage(
                        f"Modular input `{modular_input.name} does not specify a `python.version`, and "
                        f"the `[default]` stanza in {global_default_python.get_relative_path()} "
                        f"specifies {PYTHON_LATEST_VERSION}. "
                        f"Note that python.version={PYTHON_LATEST_VERSION} is not supported for Splunk <= 9.2.",
                        file_name=global_default_python.get_relative_path(),
                        line_number=global_default_python.get_line_number(),
                    )
            else:
                # inputs.conf does not exist or nothing specifies python.version
                section = None
                if inputs_config and inputs_config.has_section(modular_input.name):
                    section = inputs_config.get_section(modular_input.name)
                elif inputs_config and inputs_config.has_section("default"):
                    section = inputs_config.get_section("default")

                if section:
                    file_name = section.get_relative_path()
                    line_number = section.get_line_number()
                elif inputs_config:
                    file_name = inputs_config.get_relative_path()
                    line_number = None
                else:
                    file_name = "default/inputs.conf"
                    line_number = None

                yield FailMessage(
                    f"`python.version` is not specified for modular input `{modular_input.name}.",
                    file_name=file_name,
                    line_number=line_number,
                    remediation=f"Add `inputs.conf` and set `python.version` to one of: {', '.join(PYTHON_3_VERSIONS)} as required in a "
                    f"`[default]` stanza, or explicitly in a `[{modular_input.name}]` "
                    "stanza.",
                )


class CheckForScriptedInputs(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_for_scripted_inputs",
                description="Check if inputs.conf includes scripted inputs.",
                depends_on_config=("inputs",),
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    def check_config(self, app, config):
        inputs_conf = config["inputs"]
        script_stanzas = [stanza for stanza in inputs_conf.sections() if stanza.name.startswith("script://")]
        if len(script_stanzas) > 0:
            for stanza in script_stanzas:
                yield WarningMessage(
                    f"App contains a scripted input {stanza.name}. No action required.",
                    file_name=stanza.relative_path,
                    line_number=stanza.lineno,
                )
        else:
            yield NotApplicableMessage("The inputs.conf does not contain any scripted inputs.")


class CheckForModularInputs(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_for_modular_inputs",
                description="Check if inputs.conf.spec includes modular inputs.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    @Check.depends_on_files(
        basedir=["README"],
        names=["inputs.conf.spec"],
        not_applicable_message="README/inputs.conf.spec does not exist.",
    )
    def check_inputs_conf_spec(self, app: "App", path_in_app: Path):
        yield WarningMessage(
            "App contains modular inputs in inputs.conf.spec. No action required.", file_name=path_in_app
        )
