# Copyright 2024 Splunk Inc. All rights reserved.

"""
### SPL2-specific checks

This group includes checks for validating SPL2 files.
"""
import json
import re
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from lxml import etree

from splunk_appinspect.check_messages import FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.checks import CheckMessage
    from splunk_appinspect.custom_types import ConfigurationProxyType, FileViewType


class CheckRunAsOwner(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_run_as_owner",
                description="Check that no SPL2 modules have `@run_as_owner;` annotation enabled.",
                depends_on_data=("spl2",),
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

    def check_data(self, app: "App", file_view: "FileViewType") -> Generator["CheckMessage", Any, None]:
        for directory, filename, _ in file_view.iterate_files(basedir="spl2", types=[".spl2"]):
            try:
                for match in app.search_for_matches_in_file(["@run_as_owner;"], directory, filename):
                    filepath, line_no = match[0].rsplit(":", 1)
                    yield FailMessage(
                        "SPL2 modules in Splunkbase apps may not specify `@run_as_owner` directly, as this could "
                        "result in permission escalations. Comment out this line, and add documentation that "
                        "explains why running the module as the owner is necessary. Admins may choose to un-comment "
                        "this annotation.",
                        file_name=filepath,
                        line_number=line_no,
                    )
            except IOError as e:
                yield FailMessage(
                    f"Encountered IO error while reading the file: {e.strerror}.",
                    file_name=Path(directory, filename),
                )


class CheckSPL2Usage(Check):
    SPL2_QUERY_REGEX = re.compile(r"\|\s*@spl2")
    MESSAGE = "This app contains SPL2 modules and/or knowledge objects that use SPL2. No action needed."

    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_spl2_usage",
                description="Check if the app contains any SPL2 code.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ),
                depends_on_config=("savedsearches", "alert_actions"),
                depends_on_data=(Path("ui", "views"), Path("spl2"), Path("models")),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxyType") -> Generator["CheckMessage", Any, None]:
        def check_conf(conf_name: str, prop_name: str) -> Generator["CheckMessage", Any, None]:
            conf = config[conf_name]
            if conf:
                props = (section[prop_name] for section in conf.sections() if section.has_option(prop_name))
                for prop in props:
                    if self._query_is_spl2(prop.value):
                        yield WarningMessage(
                            self.MESSAGE,
                            file_name=prop.relative_path,
                            line_number=prop.lineno,
                        )

        yield from check_conf("savedsearches", "search")
        yield from check_conf("alert_actions", "command")

    def check_data(self, app: "App", file_view: "FileViewType") -> Generator["CheckMessage", Any, None]:
        # non-empty .spl2 files
        for directory, filename, _ in file_view.iterate_files("spl2", types=[".spl2"]):
            path = Path(directory, filename)
            full_path = app.get_filename(path)
            if full_path.stat().st_size > 0:
                yield WarningMessage(
                    self.MESSAGE,
                    file_name=path,
                )

        # .xml dashboards
        for directory, filename, _ in file_view.iterate_files(Path("ui", "views"), types=[".xml"]):
            path = Path(directory, filename)
            full_path = app.get_filename(path)
            try:
                root: etree.ElementBase = etree.parse(full_path).getroot()

                # legacy SXML views, global ./search/query and ./row/panel/**/search/query
                # https://docs.splunk.com/Documentation/Splunk/latest/Viz/BuildandeditdashboardswithSimplifiedXML
                for element in root.findall(".//search/query"):
                    if element.text and self._query_is_spl2(element.text):
                        yield WarningMessage(self.MESSAGE, file_name=path, line_number=element.sourceline)

                # JSON views
                # https://docs.splunk.com/Documentation/Splunk/latest/DashStudio/dashDef
                for element in root.iter("definition"):
                    json_data = json.loads(element.text)
                    data_sources = chain(
                        # dataSources{}.*.options{}.query
                        json_data.get("dataSources", {}).values(),
                        # defaults{}.dataSources{}.*.options{}.query
                        json_data.get("defaults", {}).get("dataSources", {}).values(),
                    )

                    for data_source in data_sources:
                        query = data_source.get("options", {}).get("query", None)
                        if query and self._query_is_spl2(query):
                            yield WarningMessage(self.MESSAGE, file_name=path, line_number=element.sourceline)
            except Exception as e:
                yield FailMessage(f"Failed to process file : {e}", path)
        # JSON models
        # objects[].constraints[].search
        for directory, filename, _ in file_view.iterate_files(Path("models"), types=[".json"]):
            path = Path(directory, filename)
            full_path = app.get_filename(path)
            try:
                with open(full_path, "r") as f:
                    json_data = json.load(f)

                for object in json_data.get("objects", []):
                    for constraint in object.get("constraints", []):
                        if "search" in constraint and self._query_is_spl2(constraint["search"]):
                            yield WarningMessage(
                                self.MESSAGE,
                                file_name=path,
                            )
            except Exception as e:
                yield FailMessage(f"Failed to process file : {e}", path)

    @Check.depends_on_matching_files(
        patterns=[SPL2_QUERY_REGEX],
        basedir=Path("appserver", "js"),
        types=[".js"],
    )
    def check_static_js(
        self, app: "App", path_in_app: str, line_number: int, match: "re.Match"
    ) -> Generator["CheckMessage", Any, None]:
        yield WarningMessage(self.MESSAGE, file_name=path_in_app, line_number=line_number)

    def _query_is_spl2(self, query: str):
        """Removes unnecessary whitespaces from the SPL2 query:
        1. trim
        2. remove \\\\n (literally)
        3. remove new-lines (e.g. multi-line .xml text)
        """
        query = query.strip().replace("\\n", "").replace("\n", "")
        return self.SPL2_QUERY_REGEX.match(query)
