# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Authorize.conf file standards

Ensure that the authorize configuration file located in the **/default** folder is well-formed and valid. For more, see [authorize.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/authorizeconf).
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Generator

from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.splunk_defined_authorize_capability_list import (
    SPLUNK_DEFINED_CAPABILITY_NAME,
    SPLUNK_DEFINED_WINDOWS_SPECIFIC_CAPABILITY_NAME,
)

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy


logger = logging.getLogger(__name__)


class CheckAuthorizeConfCapabilityNotModified(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_authorize_conf_capability_not_modified",
                description="Check that authorize.conf does not contain any modified capabilities. ",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
                depends_on_config=("authorize",),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for authorize in config["authorize"].sections():
            filename = config["authorize"].get_relative_path()
            if (
                authorize.name.startswith("capability::")
                and authorize.name in SPLUNK_DEFINED_CAPABILITY_NAME | SPLUNK_DEFINED_WINDOWS_SPECIFIC_CAPABILITY_NAME
            ):
                # ONLY fail if the custom capability stanza matches a Splunkwide capability
                lineno = authorize.lineno
                yield FailMessage(
                    f"The following capability was modified: {authorize.name}. "
                    "Capabilities that exist in Splunk Cloud can not be modified. ",
                    file_name=filename,
                    line_number=lineno,
                )


class CheckAuthorizeConfHasNoO11yCapabilities(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_authorize_conf_has_no_o11y_capabilities",
                description="Checks that authorize.conf has no capabilities starting with o11y_.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
                depends_on_config=("authorize",),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for authorize in config["authorize"].sections():
            filename = config["authorize"].get_relative_path()
            if authorize.name.startswith("capability::o11y_"):
                lineno = authorize.lineno
                yield FailMessage(
                    f"Found stanza [{authorize.name}]. Capabilities starting with o11y_ are reserved for o11y.",
                    file_name=filename,
                    line_number=lineno,
                )


class CheckAuthorizeConfRoleNames(Check):
    """
    Up to date with Splunk 9.3.2 authorize.conf.spec:
    https://docs.splunk.com/Documentation/Splunk/9.3.2/Admin/Authorizeconf
    """

    PATTERN = r"role_.*[A-Z:;/ ].*"

    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_authorize_conf_role_names",
                description="Checks that roles defined in `authorize.conf` match the specification.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                    Tags.MIGRATION_VICTORIA,
                ),
                depends_on_config=("authorize",),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for authorize_stanza in config["authorize"].sections():
            stanza_name = authorize_stanza.name

            if re.match(self.PATTERN, stanza_name):
                yield FailMessage(
                    f"Found a role `{stanza_name[5:]}` with forbidden characters defined in stanza `[{stanza_name}]`. Rename the role to match the specification. See: https://docs.splunk.com/Documentation/Splunk/latest/Admin/Authorizeconf  for more info.",
                    file_name=config["authorize"].get_relative_path(),
                    line_number=authorize_stanza.lineno,
                )


check_authorize_conf_has_no_user_configurable_stanza = Check.disallowed_config_stanza(
    conf_file="authorize",
    stanzas=["commands:user_configurable"],
    tags=(
        Tags.SPLUNK_APPINSPECT,
        Tags.CLOUD,
        Tags.PRIVATE_APP,
        Tags.PRIVATE_VICTORIA,
        Tags.PRIVATE_CLASSIC,
        Tags.MIGRATION_VICTORIA,
    ),
    check_name="check_authorize_conf_has_no_user_configurable_stanza",
    check_description="Check that `authorize.conf` does not contain `[commands:user_configurable]` stanza. "
    "This configuration can be used to disable `nsjail`, which is prohibited in Splunk Cloud.",
    reporter_action=FailMessage,
)
