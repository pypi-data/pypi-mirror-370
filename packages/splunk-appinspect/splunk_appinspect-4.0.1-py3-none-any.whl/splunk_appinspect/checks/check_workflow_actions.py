# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Custom workflow actions structure and standards

Custom workflow actions are defined in a **workflow_actions.conf** file in the **/default** directory of the app. For more, see [About lookups](https://docs.splunk.com/Documentation/Splunk/latest/Knowledge/Aboutlookupsandfieldactions) and [workflow_actions.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Workflow_actionsconf).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generator

from splunk_appinspect.check_messages import CheckMessage, FailMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy


logger = logging.getLogger(__name__)

report_display_order = 20


class CheckWorkflowActionsLinkUriDoesNotUseHttpProtocol(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_workflow_actions_link_uri_does_not_use_http_protocol",
                description="Check that for each workflow action in `workflow_actions.conf` the "
                "link.uri property uses the https protocol for external links. Unencrypted "
                "http is permitted for internal links.",
                depends_on_config=("workflow_actions",),
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
        for section in config["workflow_actions"].sections():
            if not section.has_option("link.uri"):
                continue

            setting = section.get_option("link.uri")
            link_uri = setting.value.strip()

            if link_uri.startswith(
                (
                    "/",
                    "./",
                    "../",
                    "http://localhost",
                    "http://127.0.0.1",
                    "localhost",
                    "127.0.0.1",
                    "https://",
                    "#",
                )
            ):
                continue

            yield FailMessage(
                f"The workflow action [{section.name}] `link.uri` property appears to be an "
                "external link that is unencrypted.",
                file_name=setting.get_relative_path(),
                line_number=setting.get_line_number(),
                remediation="Change the `link.uri` property to use https",
            )
