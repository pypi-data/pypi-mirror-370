# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Meta file standards

Ensure that all meta files located in the **/metadata** folder are well-formed and valid.
"""
from __future__ import annotations

import collections
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from re import Match
    from typing import Optional

    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import (
        ConfigurationFile,
        ConfigurationSection,
        MergedConfigurationFile,
        MergedConfigurationSection,
    )
    from splunk_appinspect.custom_types import FileViewType
    from splunk_appinspect.reporter import Reporter


report_display_order = 2
logger = logging.getLogger(__name__)

RE_META_ACCESS = re.compile(r"read:\[(?P<read>\S+)],write:\[(?P<write>\S+)]")


class CheckKosAreAccessible(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_kos_are_accessible",
                description="Check that knowledge objects with access control restrictions defined in"
                " *.meta files are accessible to customers in Splunk Cloud.",
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

    def check_metadata_file(self, app: "App", path_in_app: Path) -> Generator[CheckMessage, Any, None]:
        """Check that the `metadata/` directory only contains .meta files."""
        meta_file = None
        if app.file_exists(path_in_app):
            meta_file = app.get_meta(path_in_app.name, directory=path_in_app.parent)

        if meta_file:
            for section in meta_file.sections():
                if not section.has_option("access"):
                    continue

                access_option = section.get_option("access")
                match = _parse_meta_access(access_option.value)
                if not match:
                    continue

                read = match.group("read")
                write = match.group("write")
                if read == "admin" or write == "admin":
                    yield WarningMessage(
                        "In Splunk Cloud, customers have access to the sc_admin role instead of the admin role. "
                        "Your customers will not be able to access knowledge objects where the only assigned role is admin. "
                        "Please consider also including the sc_admin role for compatibility with Splunk Cloud.",
                        file_name=path_in_app,
                        line_number=access_option.lineno,
                    )
                elif (
                    ("admin" in read.split(",") and "sc_admin" not in read.split(","))
                    or "admin" in write.split(",")
                    and "sc_admin" not in write.split(",")
                ):
                    yield WarningMessage(
                        "The 'admin' role is not available to Splunk Cloud customers. "
                        "Please consider also including the 'sc_admin' role if you want "
                        "Splunk Cloud customer administrators to be able to access this knowledge object",
                        file_name=path_in_app,
                        line_number=access_option.lineno,
                    )


class CheckDefaultWriteAccess(Check):
    DEFAULT_STANZAS = {"default", ""}

    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_meta_default_write_access",
                description="Check that the global write access in .meta does not allow any authenticated user to write "
                "to the knowledge objects under the application.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    def check_metadata(
        self, app: "App", meta: "ConfigurationFile" | "MergedConfigurationFile"
    ) -> Generator["CheckMessage", Any, None]:
        # preserve order, later section overrides the previous one
        sections = [s for s in meta.sections() if s.name in self.DEFAULT_STANZAS and s.has_option("access")]

        if len(sections) == 0:
            file_path = meta.get_relative_path()
            if file_path.name == "default.meta":
                # local.meta are allowed not to define default write access
                yield FailMessage(
                    "Metadata file does not define the global write access.",
                    remediation="Add a global write access configuration with at least one role.",
                    file_name=file_path,
                )
        else:
            report_message = self._check_section(sections[-1])
            if report_message:
                yield report_message

    def _check_section(
        self, section: "ConfigurationSection" | "MergedConfigurationSection"
    ) -> Optional["CheckMessage"]:
        access_option = section.get_option("access")
        access_parsed = _parse_meta_access(access_option.value)
        if access_parsed is None:
            return FailMessage(
                "Metadata file does not define the global write access.",
                remediation="Add a write configuration with at least one role to access settings in the global stanza.",
                file_name=access_option.get_relative_path(),
                line_number=access_option.get_line_number(),
            )

        write_roles = map(str.strip, access_parsed.group("write").split(","))
        if "*" in write_roles:
            return FailMessage(
                "Metadata file allows any user to write to any knowledge object.",
                remediation="Add a write configuration with at least one role to the access settings in the global stanza.",
                file_name=access_option.get_relative_path(),
                line_number=access_option.get_line_number(),
            )

        return None


def _parse_meta_access(access_value: str) -> Optional[Match[str]]:
    return RE_META_ACCESS.match(access_value.replace(" ", ""))
