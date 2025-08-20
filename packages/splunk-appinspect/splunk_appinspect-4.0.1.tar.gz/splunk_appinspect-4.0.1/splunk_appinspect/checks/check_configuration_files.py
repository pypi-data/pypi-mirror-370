# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Configuration file standards

Ensure that all configuration files located in the **/default** folder are well-formed and valid.
"""
from __future__ import annotations

import collections
import itertools
import logging
import os.path
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect import App, app_util
from splunk_appinspect.check_messages import CheckMessage, FailMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.splunk_defined_conf_file_list import SPLUNK_DEFINED_CONFS

if TYPE_CHECKING:
    from splunk_appinspect.configuration_file import ConfigurationProxy, ConfigurationSection
    from splunk_appinspect.reporter import Reporter

report_display_order = 2
logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_config_file_parsing(app: "App", reporter: "Reporter") -> None:
    """Check that all config files parse cleanly - no trailing whitespace after
    continuations, no duplicated stanzas or options.
    """
    basedir = ["default", "local", *app.get_user_paths("local")]
    for directory, filename, _ in app.iterate_files(types=[".conf"], basedir=basedir):
        try:
            file_path = Path(directory, filename)
            conf = app.get_config(filename, dir=directory)
            for err, lineno, section in conf.errors:
                reporter_output = (
                    f"{err} at line {lineno} in [{section}] of {filename}. " f"File: {file_path}, Line: {lineno}."
                )
                reporter.fail(reporter_output, file_path, lineno)
        except Exception as error:
            logger.error("unexpected error occurred: %s", str(error))
            raise


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
)
def check_config_file_parsing_public(app: "App", reporter: "Reporter", included_tags: list[Tags]) -> None:
    """Check that all config files parse cleanly - no trailing whitespace after
    continuations, no duplicated stanzas or options.
    """
    for directory, filename, _ in app.iterate_files(types=[".conf"], basedir=["default", "local"]):
        try:
            file_path = Path(directory, filename)
            conf = app.get_config(filename, dir=directory)
            for err, lineno, section in conf.errors:
                reporter_output = (
                    f"{err} at line {lineno} in [{section}] of {filename}. " f"File: {file_path}, Line: {lineno}."
                )
                if err.startswith(("Duplicate stanza", "Repeat item")):
                    reporter.warn(reporter_output, file_path, lineno)
                    continue
                reporter.fail(reporter_output, file_path, lineno)
        except Exception as error:
            logger.error("unexpected error occurred: %s", str(error))
            raise


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_no_default_stanzas(app: "App", reporter: "Reporter") -> None:
    """Check that app does not contain any .conf files that create global
    definitions using the `[default]` stanza.
    """
    # Added allow list support because people are making poor life choices and
    # building splunk features that require the use of the `default` stanza
    # The white list conf files using the default stanza will be supported, but
    # not condoned
    conf_file_allow_list = {"savedsearches.conf"}
    # it is common for user-prefs.conf to have [default] stanza
    stanza_allow_list = {("user-prefs.conf", "general")}
    default_stanzas = ["default", "general", "global", "stash"]
    conf_locations = ["default", "local", *app.get_user_paths("local")]

    def is_splunk_defined_conf(conf_tuple):
        return conf_tuple[1] in SPLUNK_DEFINED_CONFS and conf_tuple[1] not in conf_file_allow_list

    def to_conf(conf_tuple):
        directory, filename, _ = conf_tuple
        return app.get_config(filename, dir=directory)

    def conf_has_non_empty_section(conf_section):
        conf, section = conf_section
        return conf.has_section(section) and len(conf.get_section(section).items()) > 0

    def section_not_in_allowlist(conf_section):
        conf, section = conf_section
        return (conf.relative_path.name, section) not in stanza_allow_list

    conf_files = filter(is_splunk_defined_conf, app.iterate_files(types=[".conf"], basedir=conf_locations))
    conf_files = map(to_conf, conf_files)
    conf_stanza_pairs = itertools.product(conf_files, default_stanzas)
    conf_stanza_pairs = filter(conf_has_non_empty_section, conf_stanza_pairs)
    conf_stanza_pairs = filter(section_not_in_allowlist, conf_stanza_pairs)

    for conf, section_name in conf_stanza_pairs:
        lineno = conf.get_section(section_name).lineno
        reporter.fail(
            f"{section_name} stanza was found in {conf.relative_path}. "
            "Please remove any [default], [general], [global], [stash] stanzas or properties "
            "outside of a stanza (treated as default/global) "
            "from conf files defined by Splunk. "
            "These stanzas/properties are not permitted "
            "because they modify global settings outside the context of the app.",
            file_name=conf.relative_path,
            line_number=lineno,
        )


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_manipulation_outside_of_app_container(app: "App", reporter: "Reporter") -> None:
    """Check that app conf files do not point to files outside the app container.
    Because hard-coded paths won't work in Splunk Cloud, we don't consider to
    check absolute paths.
    """
    reporter_template = (
        "Manipulation outside of the app container was found in "
        "file {}; See stanza `{}`, "
        "key `{}` value `{}`. File: {}, Line: {}."
    )
    app_name = app.package.working_artifact_name

    conf_parameter_arg_regex = re.compile(r""""[^"]+"|'[^']+'|[^"'\s]+""")
    conf_check_list = {
        "app.conf": ["verify_script"],
        "distsearch.conf": ["genKeyScript"],
        "restmap.conf": ["pythonHandlerPath"],
        "authentication.conf": ["scriptPath"],
        "server.conf": ["certCreateScript"],
        "limits.conf": ["search_process_mode"],
    }
    basedir = ["default", "local", *app.get_user_paths("local")]
    for directory, filename, _ in app.iterate_files(types=[".conf"], basedir=basedir):
        if filename not in conf_check_list:
            continue
        conf = app.get_config(filename, dir=directory)
        for section in conf.sections():
            full_filepath = Path(directory, filename)
            for option in section.settings():
                key = option.name
                value = option.value
                lineno = option.lineno
                if key not in conf_check_list[filename]:
                    continue
                for path in conf_parameter_arg_regex.findall(value):
                    if app_util.is_manipulation_outside_of_app_container(path, app_name):
                        reporter_output = reporter_template.format(
                            full_filepath,
                            section.name,
                            key,
                            value,
                            full_filepath,
                            lineno,
                        )
                        reporter.fail(reporter_output, full_filepath, lineno)


class CheckCollectionsConfForSpecifiedNameFieldType(Check):
    VALID_FIELD_TYPES = set(["bool", "number", "string", "time"])

    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_collections_conf_for_specified_name_field_type",
                description="Check that the field type in `field.<name>` settings in `collections.conf` is valid. "
                "Only `number`, `bool`, `string` and `time` are allowed.",
                depends_on_config=("collections",),
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
        for section in config["collections"].sections():
            for key, value in iter(section.options.items()):
                if not key.startswith("field."):
                    continue
                value = value.value.split("#")[0].strip()
                if value not in self.VALID_FIELD_TYPES:
                    yield FailMessage(
                        "The field type in `field.<name>` settings in `collections.conf` only allows "
                        f"`number`, `bool`, `string` or `time` values but found `{value}` in `{key}`.",
                        file_name=config["collections"].get_relative_path(),
                        line_number=config["collections"][section.name][key].get_line_number(),
                    )
