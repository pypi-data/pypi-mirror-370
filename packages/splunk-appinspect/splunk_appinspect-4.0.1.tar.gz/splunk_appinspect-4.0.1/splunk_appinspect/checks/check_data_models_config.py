# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Data model files and configurations

Data models are defined in a **datamodels.conf** file in the **/default** directory of the app. For more, see [About data models](https://docs.splunk.com/Documentation/Splunk/latest/Knowledge/Aboutdatamodels) and [datamodels.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Datamodelsconf).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.splunk import normalizeBoolean

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.reporter import Reporter


report_display_order = 25
logger = logging.getLogger(__name__)


class CheckForDatamodelAcceleration(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_datamodel_acceleration",
                description="Check that the use of accelerated data models do not occur. If data model "
                "acceleration is required, developers should provide directions in documentation "
                "for how to accelerate data models from within the Splunk Web GUI. "
                "[data model acceleration](https://docs.splunk.com/Documentation/Splunk/latest/Knowledge/Acceleratedatamodels)",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
                depends_on_config=("datamodels",),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        datamodels_config = config["datamodels"]

        # check if acceleration=true is set in default stanza
        is_default_stanza_accelerated = False
        if datamodels_config.has_section("default") and datamodels_config.has_option("default", "acceleration"):
            accelerated = datamodels_config.get("default", "acceleration")
            is_default_stanza_accelerated = normalizeBoolean(accelerated)

        for section in config["datamodels"].sections():
            is_accelerated = False
            lineno = None
            if section.name != "default":
                if section.has_option("acceleration"):
                    if normalizeBoolean(section.get_option("acceleration").value):
                        is_accelerated = True
                        lineno = section.get_option("acceleration").lineno

                elif is_default_stanza_accelerated:
                    is_accelerated = True
                    lineno = datamodels_config.get_section("default").get_option("acceleration").lineno

                if is_accelerated:
                    yield FailMessage(
                        f"Data model acceleration was detected for stanza [{section.name}.",
                        file_name=datamodels_config.get_relative_path(),
                        line_number=lineno,
                        remediation=f"Set `acceleration = false` for [{section.name}]. "
                        "If data model acceleration is required, please provide users with "
                        "guidance on how to enable data model acceleration from within the "
                        "Splunk Web GUI.",
                    )
                else:
                    yield WarningMessage(
                        f"Data model [{section.name}] was detected in this app and can eat disk space. ",
                        file_name=datamodels_config.get_relative_path(),
                        line_number=lineno,
                    )
