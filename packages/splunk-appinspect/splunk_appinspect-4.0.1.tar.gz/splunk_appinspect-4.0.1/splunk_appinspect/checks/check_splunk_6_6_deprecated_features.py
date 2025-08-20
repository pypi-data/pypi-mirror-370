# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated or removed features from Splunk Enterprise 6.6

The following features should not be supported in Splunk 6.6 or later. For more, see [Deprecated features](https://docs.splunk.com/Documentation/Splunk/6.6.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](https://docs.splunk.com/Documentation/Splunk/6.6.0/Installation/ChangesforSplunkappdevelopers).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generator

from semver import VersionInfo

import splunk_appinspect
from splunk_appinspect import App, check_routine
from splunk_appinspect.check_messages import CheckMessage, FailMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.reporter import Reporter


logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.AST,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_app_install_endpoint(app: "App", reporter: "Reporter") -> None:
    """Check apps/appinstall usages"""
    reporter_output = (
        "apps/appinstall endpoint has been deprecated in Splunk 6.6. "
        "And it might be removed entirely in a future release. An alternative could be found at"
        "https://answers.splunk.com/answers/512205/"
        "how-do-i-install-an-app-via-rest-using-the-appsloc.html#answer-512206"
    )

    kws = ["apps/appinstall"]
    regex_file_types = [".js", ".html", ".xml", ".conf"]

    for matched_file, matched_lineno in check_routine.find_endpoint_usage(
        app=app, kws=kws, regex_file_types=regex_file_types
    ):
        reporter.fail(reporter_output, matched_file, matched_lineno)


class CheckForAutolbSettingInOutputsConf(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_autolb_setting_in_outputs_conf",
                description="Check removed support for setting autoLB in outputs.conf",
                depends_on_config=("outputs",),
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

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for section in config["outputs"].sections():
            if config["outputs"].has_option(section.name, "autoLB"):
                yield FailMessage(
                    "Removed support for setting autoLB in outputs.conf, "
                    "since autoLB can only be true, as there is no other "
                    "method for forwarding data to indexers.",
                    file_name=config["outputs"].get_relative_path(),
                    line_number=config["outputs"][section.name]["autoLB"].get_line_number(),
                )


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_displayrownumbers_in_simple_xml(app: "App", reporter: "Reporter") -> None:
    """
    Check existence for displayRowNumbers option in simple xml. This option
    is no longer supported since Splunk 6.6.
    """
    # This check will examine <option name="displayRowNumbers">true</option> in simple xml.
    # There is another two uses of displayRowNumbers as the following:
    # 1:(in advanced xml)
    #      <module name="SimpleResultsTable" layoutPanel="panel_row1_col1">
    #          <param name="displayRowNumbers">False</param>
    #      </module>
    # 2:(in viewstates.conf)
    #      RowNumbers_x_x_x.displayRowNumbers = xxxx in viewstates.conf
    # However, for case 1, <module> tag is deprecated(as part of the deprecation of AXML,
    # covered by check_for_advanced_xml_module_elements). For case 2, viewstates.conf is deprecated
    # (covered by check_for_viewstates_conf).
    # Therefore, we'll omit these two cases.
    reporter_output = (
        "<option> elements with the attribute [name=displayRowNumbers] was detected, "
        "which has been removed since Splunk 6.6. Please do not use it."
    )
    option_node = check_routine.xml_node("option")
    option_node.attrs = {"name": "displayRowNumbers"}
    check_routine.report_on_xml_findings(
        check_routine.find_xml_nodes(app, [option_node]),
        reporter,
        reporter_output,
        reporter.fail,
    )
