# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Authentication.conf file standards

Ensure that `bindDNpassword` is not specified. For more, see [authentication.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Authenticationconf).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import PYTHON_3_VERSIONS, PYTHON_LATEST_VERSION, Tags
from splunk_appinspect.splunk import normalizeBoolean

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.reporter import Reporter


if TYPE_CHECKING:
    from splunk_appinspect.configuration_file import ConfigurationSection

logger = logging.getLogger(__name__)


class CheckSamlAuthShouldNotTurnOffSignedAssertion(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_saml_auth_should_not_turn_off_signed_assertion",
                description="Check that saml-* stanzas in `authentication.conf` do not turn off signedAssertion property. ",
                depends_on_config=("authentication",),
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

    def _is_signed_assertion_off(self, section: ConfigurationSection) -> bool:
        return not normalizeBoolean(section.get_option("signedAssertion").value.strip())

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        auth_conf = config["authentication"]
        if config["authentication"].has_option("authentication", "authType"):
            auth_type_value = auth_conf.get("authentication", "authType")

            if auth_type_value == "SAML":
                stanzas_with_signed_assertion = [
                    (section.name, section.lineno)
                    for section in auth_conf.sections_with_setting_key_pattern("signedAssertion")
                    if section.name.startswith("saml-") and self._is_signed_assertion_off(section)
                ]
                for stanza_name, stanza_lineno in stanzas_with_signed_assertion:
                    yield FailMessage(
                        "SAML signedAssertion property is turned off, which will introduce vulnerabilities. "
                        "Please turn the signedAssertion property on. "
                        f"Stanza: [{stanza_name}] ",
                        file_name=auth_conf.get_relative_path(),
                        line_number=stanza_lineno,
                    )


class CheckScriptedAuthenticationHasValidPythonVersionProperty(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_scripted_authentication_has_valid_python_version_property",
                description="Check that all the scripted authentications defined in `authentication.conf` "
                f"explicitly set the python.version to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                depends_on_config=("authentication",),
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
        auth_conf = config["authentication"]

        if (
            auth_conf.has_option("authentication", "authType")
            and auth_conf.get("authentication", "authType") == "Scripted"
            and auth_conf.has_option("authentication", "authSettings")
        ):
            auth_settings_stanza_name = auth_conf.get("authentication", "authSettings")
            if auth_conf.has_section(auth_settings_stanza_name):
                python_version = None
                if auth_conf.has_option(auth_settings_stanza_name, "python.version"):
                    python_version = auth_conf.get(auth_settings_stanza_name, "python.version")
                if (
                    not python_version
                    or python_version != PYTHON_LATEST_VERSION
                    and python_version not in PYTHON_3_VERSIONS
                ):
                    yield FailMessage(
                        f"Scripted authentication [{auth_settings_stanza_name}] is defined, "
                        f"and python.version should be explicitly set "
                        f"to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                        file_name=config["authentication"].get_relative_path(),
                        line_number=config["authentication"][auth_settings_stanza_name].get_line_number(),
                    )
                    return
                elif python_version == PYTHON_LATEST_VERSION:
                    yield WarningMessage(
                        f"Scripted authentication [{auth_settings_stanza_name}] is defined, "
                        f"and `python.version` is set to {PYTHON_LATEST_VERSION}. "
                        f"Note that python.version={PYTHON_LATEST_VERSION} is not supported for Splunk <= 9.2.",
                        file_name=config["authentication"].get_relative_path(),
                        line_number=config["authentication"][auth_settings_stanza_name].get_line_number(),
                    )
                    return
            else:
                yield WarningMessage(
                    f"Script authentication configuration for [{auth_settings_stanza_name}] is missing. "
                )


class CheckRoleMapShouldNotMapSplunkSystemRole(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_role_map_should_not_map_splunk_system_role",
                description="Check that all map roles defined in `authentication.conf` "
                "do not map to `splunk-system-role`.",
                depends_on_config=("authentication",),
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

    ROLE_MAP_PREFIX = "roleMap_"
    SPLUNK_SYSTEM_ROLE = "splunk-system-role"

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        auth_conf = config["authentication"]
        for section in auth_conf.sections():
            if section.name.startswith(self.ROLE_MAP_PREFIX) and section.has_option(self.SPLUNK_SYSTEM_ROLE):
                yield FailMessage(
                    f"Mapping role to splunk-system-role is not allowed. Stanza: [{section.name}].",
                    file_name=auth_conf.get_relative_path(),
                    line_number=auth_conf[section.name].get_line_number(),
                )


check_for_o11y_roles = Check.disallowed_config_stanza(
    conf_file="authorize",
    stanzas=["o11y_admin", "o11y_power", "o11y_read_only", "o11y_usage"],
    tags=(
        Tags.SPLUNK_APPINSPECT,
        Tags.CLOUD,
        Tags.PRIVATE_APP,
        Tags.PRIVATE_VICTORIA,
        Tags.MIGRATION_VICTORIA,
        Tags.PRIVATE_CLASSIC,
    ),
    check_name="check_for_o11y_roles",
    check_description="Check that authorize.conf does not contain any o11y role stanzas. "
    "O11y role is one of o11y_admin, o11y_power, o11y_read_only or o11y_usage.",
)
