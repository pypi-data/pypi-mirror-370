# Copyright 2024 Splunk Inc. All rights reserved.

"""
### Universal Configuration Console standards
"""
import ast
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import yaml

from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect.app import App

report_display_order = 50
logger = logging.getLogger(__name__)


class GlobalConfigReader(ABC):
    def __init__(self, path: Path):
        self.path = path

    @abstractmethod
    def read_file(self) -> dict:
        pass


class JsonGlobalConfigReader(GlobalConfigReader):
    def read_file(self) -> dict:
        with open(self.path, "r") as file:
            return json.load(file)


class YamlGlobalConfigReader(GlobalConfigReader):
    def read_file(self) -> dict:
        with open(self.path, "r") as file:
            return yaml.safe_load(file)


class CheckForUCCFrameworkVersion(Check):
    BUILD_PATH = Path("appserver", "static", "js", "build")

    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_ucc_framework_version",
                description="Check UCC framework version.",
                tags=(Tags.SPLUNK_APPINSPECT,),
            )
        )

    @Check.depends_on_files(
        basedir=[BUILD_PATH],
        names=["globalConfig.json", "globalConfig.yaml"],
        not_applicable_message="No UCC framework found.",
    )
    def check_for_ucc_framework_version(self, app: "App", path_in_app: str) -> Generator[CheckMessage, Any, None]:
        full_filepath = app.get_filename(path_in_app)
        reader = self._get_data_reader(full_filepath)
        try:
            data = reader.read_file()
        except Exception as e:
            yield FailMessage(f"Failed to process file: {e}. File: {path_in_app}", file_name=path_in_app)
            return

        ucc_version = yield from self._get_ucc_version(data)

        if not ucc_version:
            yield NotApplicableMessage("No version found in globalConfig file.")
            return

        yield WarningMessage(f"UCC framework usage detected. version = {ucc_version}.")

    @staticmethod
    def _get_ucc_version(data):
        metadata = data.get("meta")
        if not metadata:
            yield NotApplicableMessage("No metadata section found in globalConfig file.")
            return
        ucc_version = metadata.get("_uccVersion")
        return ucc_version

    @staticmethod
    def _get_data_reader(path_in_app: Path) -> GlobalConfigReader:
        if path_in_app.suffix == ".json":
            reader = JsonGlobalConfigReader(path_in_app)
        else:
            reader = YamlGlobalConfigReader(path_in_app)
        return reader


class CheckUCCDependencies(Check):
    CHECK_FOR_LIBRARIES = ["solnlib", "splunktaucclib"]

    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_ucc_dependencies",
                description="Check UCC dependencies versions.",
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

    @Check.depends_on_files(basedir=["lib", "bin"], names=["__init__.py"])
    def check_ucc_dependencies(self, app: "App", path_in_app: Path) -> Generator[CheckMessage, Any, None]:
        library_name = path_in_app.parts[-2]

        if library_name not in self.CHECK_FOR_LIBRARIES:
            return

        version_node = app.python_analyzer_client.get_ast_info(path_in_app).module.global_map.get("__version__")

        if version_node is None:
            return

        version_str = version_node.variable_value
        version_lineno = (
            version_node.variable_value_node.lineno if isinstance(version_node.variable_value_node, ast.expr) else None
        )

        if version_str is not None:
            yield WarningMessage(
                f"Detected {library_name} (version {version_str}). No action required.",
                file_name=path_in_app,
                line_number=version_lineno,
            )
