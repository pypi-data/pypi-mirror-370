# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Lookup file standards

Lookups add fields from an external source to events based on the values of fields that are already present in those events.
"""
from __future__ import annotations

import glob
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect import App, lookup
from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.reporter import Reporter


logger = logging.getLogger(__name__)
report_display_order = 13


class CheckForLookupsFileName(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_lookups_file_name",
                description="Check that no two files/directories under the lookups directory have this naming pattern respectively:"
                "`xxx` and `xxx.default` - with the only difference in the `.default` extension."
                "During the installation of an app in Splunk Cloud, a lookup file will be temporarily renamed to append an additional"
                "`.default` extension to it, which will cause error if a namesake file already exists.",
                depends_on_config=("app",),
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
        def is_preserve_lookups_mode(config: "ConfigurationProxy") -> bool:
            app_conf = config["app"]
            if app_conf.has_section("shclustering") and app_conf["shclustering"].has_option(
                "deployer_lookups_push_mode"
            ):
                if app_conf["shclustering"]["deployer_lookups_push_mode"].value == "always_overwrite":
                    return False
            return True

        if app.directory_exists("lookups"):
            base_dir = Path(app.app_dir, "lookups")

            if not is_preserve_lookups_mode(config):
                return

            for path in glob.glob(str(base_dir.joinpath("*.default"))):
                csv_path = path[: -len(".default")]
                if os.path.exists(csv_path):
                    default_file = os.path.basename(path)
                    csv_file = os.path.basename(csv_path)
                    default_path = Path("lookups", default_file)
                    yield FailMessage(
                        f"When installing an app in Splunk Cloud, the lookup file '{csv_file}'"
                        " will be temporarily renamed with an extra '.default' extension."
                        f" It will run into errors if '{default_file}' file already exists.",
                        file_name=default_path,
                        remediation="Please remove one of these files or change one of their names.",
                    )

        else:
            yield NotApplicableMessage(
                "lookups folder does not exist",
            )
