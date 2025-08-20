# Copyright 2019 Splunk Inc. All rights reserved.

"""
### REST endpoints and handler standards

REST endpoints are defined in a **restmap.conf** file in the **/default** and **/local** directory of the app. For more, see [restmap.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Restmapconf).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generator, Type

from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import PYTHON_3_VERSIONS, PYTHON_LATEST_VERSION, Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.custom_types import ConfigurationProxyType


logger = logging.getLogger(__name__)

report_display_order = 23


class CheckRestmapConfExists(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_restmap_conf_exists",
                description="Check that `restmap.conf` file exists at `default/restmap.conf`, `local/restmap.conf` "
                "and users/<username>/local/restmap.conf` when using REST endpoints.",
                depends_on_config=("restmap",),
                report_display_order=1,
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

    def check_config(self, app: "App", config: "ConfigurationProxyType") -> Generator[CheckMessage, Any, None]:
        if "restmap" not in config:
            yield NotApplicableMessage(
                "No restmap.conf file exists.",
            )


def do_rest_handler_scripts_check(
    app: "App", result_message: Type[CheckMessage], config: "ConfigurationProxy"
) -> Generator[CheckMessage, Any, None]:
    """Check that each stanza in restmap.conf has a matching handler script."""
    rest_map = app.get_rest_map(config)
    # From ACD-300, ACD-271,ACD-367
    # A rest config can have both, handler and handler_file. Or use the global handler
    # See
    # http://docs.splunk.com/Documentation/Splunk/latest/Admin/restmapconf
    global_handler = rest_map.global_handler_file()

    if global_handler.exists():
        message = f"A global rest handler was found at {global_handler.file_path}"
        logger.info(message)

    else:
        logger.info("A global rest handler was not found at %s", global_handler.file_path)

        handler_list = rest_map.handlers()
        for handler in handler_list:
            if (
                handler.handler_file().exists()
                or handler.handler().exists()
                or handler.executable_script_file().exists()
            ):
                pass
            else:
                yield result_message(
                    f"Neither the handler or handlerfile specified in the stanza {handler.name} was found"
                    f" in app/bin for {handler.handler_file().file_path}, {handler.handler().file_path} or"
                    f" {handler.executable_script_file().file_path}.",
                    file_name=config["restmap"].get_relative_path(),
                    line_number=config["restmap"][handler.name].get_line_number(),
                )


class CheckRestHandlerScriptsExistForCloud(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_rest_handler_scripts_exist_for_cloud",
                description="Check that each stanza in restmap.conf has a matching handler script.",
                depends_on_config=("restmap",),
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

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        yield from do_rest_handler_scripts_check(app, FailMessage, config)


class CheckRestHandlerPythonExecutableExists(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_rest_handler_python_executable_exists",
                description=f"Check that `python.version` is set to one of: {', '.join(PYTHON_3_VERSIONS)} as required, for executables in restmap.conf.",
                depends_on_config=("restmap",),
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

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        rest_map = app.get_rest_map(config)
        handler_list = rest_map.handlers()
        for handler in handler_list:
            # Skip non-python rest handler. It is reasonable to assume that Python files will have .py extension.
            if handler.script_type == "persist" and not handler.handler_module_file_name.suffix.endswith(".py"):
                continue

            # Verify python rest handler.
            if (
                not handler.python_version
                or handler.python_version != PYTHON_LATEST_VERSION
                and handler.python_version not in PYTHON_3_VERSIONS
            ):
                yield FailMessage(
                    f"The handler of stanza [{handler.name}] should have `python.version` "
                    f"property set to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                    file_name=config["restmap"].get_relative_path(),
                    line_number=config["restmap"][handler.name].get_line_number(),
                )
            elif handler.python_version == PYTHON_LATEST_VERSION:
                yield WarningMessage(
                    f"The handler of stanza [{handler.name}] have `python.version` "
                    f"property set to {PYTHON_LATEST_VERSION}. "
                    f"Note that python.version={PYTHON_LATEST_VERSION} is not supported for Splunk <= 9.2.",
                    file_name=config["restmap"].get_relative_path(),
                    line_number=config["restmap"][handler.name].get_line_number(),
                )
