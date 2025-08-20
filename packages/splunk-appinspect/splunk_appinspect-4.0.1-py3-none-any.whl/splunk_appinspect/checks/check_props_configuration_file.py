# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Props Configuration file standards

Ensure that all props.conf files located in the `default` (or `local`) folder are well-formed and valid.

- [props.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Propsconf)
- [transforms.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Transformsconf)
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.configuration_file import ConfigurationFile, ConfigurationProxy, ConfigurationSection
from splunk_appinspect.constants import Tags
from splunk_appinspect.splunk_pretrained_sourcetypes_list import SPLUNK_PRETRAINED_SOURCETYPES

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.reporter import Reporter


report_display_order = 2
logger = logging.getLogger(__name__)


class CheckPretrainedSourcetypesHaveOnlyAllowedTransforms(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_pretrained_sourcetypes_have_only_allowed_transforms",
                description="Check that pretrained sourctypes in props.conf"
                "have only 'TRANSFORM-' or 'SEDCMD' settings,"
                "and that those transforms only modify the host, source, or sourcetype.",
                depends_on_config=("props",),
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
                report_display_order=2,
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        allowed_dest_keys = ["MetaData:Host", "MetaData:Source", "MetaData:Sourcetype"]
        pretrained_sourcetype_sections = []
        for section in config["props"].sections():
            if section.name in SPLUNK_PRETRAINED_SOURCETYPES:
                pretrained_sourcetype_sections.append(section)

        # do the checking
        for section in pretrained_sourcetype_sections:
            for setting in section.settings():
                # these sections must have only "TRANSFORM-" or "SEDCMD-" settings
                if not setting.name.startswith("TRANSFORMS-") and not setting.name.startswith("SEDCMD"):
                    yield WarningMessage(
                        "Only TRANSFORMS- or SEDCMD options are allowed for pretrained sourcetypes.",
                        file_name=config["props"].get_relative_path(),
                        line_number=setting.lineno,
                    )
                    return
                if setting.name.startswith("TRANSFORMS-"):
                    if "transforms" in config:
                        for transform_stanza_name in setting.value.replace(" ", "").split(","):
                            if not config["transforms"].has_section(transform_stanza_name):
                                yield WarningMessage(
                                    f"Transforms.conf does not contain a [{transform_stanza_name.strip()}] stanza"
                                    f"to match props.conf [{section.name}] {setting.name}={setting.value}",
                                    file_name=config["props"].get_relative_path(),
                                    line_number=setting.lineno,
                                    remediation=f"Add a [{transform_stanza_name.strip()}] stanza to transforms.conf",
                                )
                                return
                            transforms_section = config["transforms"].get_section(transform_stanza_name)
                            if transforms_section.has_option("DEST_KEY"):
                                dest = transforms_section.get_option("DEST_KEY")
                                if dest.value not in allowed_dest_keys:
                                    yield WarningMessage(
                                        f"Modifying the {dest.value} field for "
                                        "a pretrained sourcetype is not allowed.",
                                        file_name=config["transforms"].get_relative_path(),
                                        line_number=dest.lineno,
                                    )
                    else:
                        yield WarningMessage(
                            "No transforms.conf exists for setting in " f"props.conf: {setting.name}={setting.value}",
                            file_name=config["props"].get_relative_path(),
                            line_number=setting.lineno,
                        )


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
)
def check_props_conf_has_no_ingest_eval_lookups(app, reporter):
    """Check that the `props.conf` does not contain `lookup()` usage in `INGEST_EVAL` options.
    This feature is not available in Splunk Cloud.

    For example:

    [lookup1]
    INGEST_EVAL= status_detail=lookup("http_status.csv", json_object("status", status), json_array("status_description"))
    """
    basedir = ["default", "local", *app.get_user_paths("local")]
    config_file_paths = app.get_config_file_paths("props.conf", basedir=basedir)
    if config_file_paths:
        found_any_settings = False
        prop_name = "INGEST_EVAL"
        value_pattern = re.compile(r".*lookup\s*\(.*")
        for directory, filename in config_file_paths.items():
            props_conf = app.props_conf(directory)

            for section in props_conf.sections_with_setting_key_pattern(prop_name, case_sensitive=True):
                found_any_settings = True
                for setting in section.settings_with_key_pattern(prop_name):
                    if value_pattern.match(setting.value):
                        file_path = Path(directory, filename)
                        reporter_output = (
                            f"Found lookup() usage in [{section.name}], {setting.name}. "
                            f"File: {file_path}, Line: {section.lineno}."
                        )
                        reporter.fail(reporter_output, file_path, section.lineno)

        if not found_any_settings:
            reporter.not_applicable("No INGEST_EVAL properties were declared.")
    else:
        reporter.not_applicable("No props.conf file exists.")


class CheckPropsConfHasNoProhibitedCharactersInSourcetypes(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_props_conf_has_no_prohibited_characters_in_sourcetypes",
                description="Check that the sourcetypes in props.conf do not contain any special characters. "
                "Sourcetypes with names containing <>?&# might not be visible.",
                depends_on_config=("props",),
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
        substrings = ("host::", "source::", "delayedrule::", "rule::")
        prohibited_chars = "<>?&#"

        for section in config["props"].sections():
            # Stanzas containing one of these substrings are allowed to have prohibited characters
            if any(substr in section.name for substr in substrings):
                continue

            if any(char in section.name for char in prohibited_chars):
                yield WarningMessage(
                    f"Found a special character in [{section.name}] stanza in props.conf. "
                    f"Sourcetype names containing <>?&# might not be visible.",
                    file_name=config["props"].get_relative_path(),
                    line_number=section.lineno,
                    remediation="Rename the stanza to not contain any special characters.",
                )


class CheckPropsConfUnarchiveCmdIsNotSet(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_props_conf_unarchive_cmd_is_not_set",
                description="Check that `props.conf` does not contain `unarchive_cmd` settings with `invalid_cause`"
                " set to `archive`.",
                depends_on_config=("props",),
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_APP,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        props_conf = config["props"]

        for section in props_conf.sections():
            if (
                section.name.startswith("source::")
                and section.has_option("unarchive_cmd")
                and section.has_option("sourcetype")
            ):
                sourcetype_stanza = section.get_option("sourcetype").value
                if props_conf.has_option(sourcetype_stanza, "invalid_cause"):
                    if props_conf.get(sourcetype_stanza, "invalid_cause") == "archive":
                        yield FailMessage(
                            f"Found `unarchive_cmd` property in [{section.name}] stanza. This setting is not "
                            f"allowed in Splunk Cloud.",
                            file_name=props_conf.get_relative_path(),
                            line_number=section.lineno,
                            remediation="Remove `unarchive_cmd` property or change the corresponding `invalid_cause`"
                            " property to anything else except `archive`.",
                        )
