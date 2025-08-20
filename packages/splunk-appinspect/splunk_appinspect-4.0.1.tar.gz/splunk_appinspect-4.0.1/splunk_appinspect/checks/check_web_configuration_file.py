# Copyright 2019 Splunk Inc. All rights reserved.
"""
### Web.conf File Standards
Ensure that `web.conf` is safe for cloud deployment and that any exposed
patterns match endpoints defined by the app - apps should not expose endpoints
other than their own.
Including `web.conf` can have adverse impacts for cloud. Allow only
`[endpoint:*]` and `[expose:*]` stanzas, with expose only containing pattern=
and methods= properties.
- [web.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Webconf)
"""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy


class CheckCherrypyControllers(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_cherrypy_controllers",
                description="Check that web.conf does not contain any custom CherryPy controllers.",
                depends_on_config=("web",),
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
        conf_file = config["web"]

        for section in config["web"].sections():
            if section.name.strip().startswith("endpoint:"):
                yield WarningMessage(
                    "Found a custom CherryPy controller. CherryPy controllers are deprecated due to added complexity in app and platform upgrades, security and performance.",
                    file_name=conf_file.get_relative_path(),
                    line_number=conf_file[section.name].get_line_number(),
                    remediation=f"Remove [{section.name}] stanza.",
                )


class CheckWebConf(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_web_conf",
                description="Check that `web.conf` only defines [endpoint:*] and [expose:*]"
                "stanzas, with [expose:*] only containing `pattern=` and `methods=`.",
                depends_on_config=("web",),
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
        filename = config["web"].get_relative_path()
        for section in config["web"].sections():
            lineno = config["web"][section.name].get_line_number()
            if not section.name.startswith("endpoint:") and not section.name.startswith("expose:"):
                yield FailMessage(
                    "Only the [endpoint:*] and [expose:*] stanzas are permitted in web.conf.",
                    file_name=filename,
                    line_number=lineno,
                    remediation=f"Remove this `[{section.name}] stanza.",
                )
            elif section.name.startswith("endpoint:"):
                endpoint_name = section.name.split("endpoint:")[1] or "<NOT_FOUND>"
                script_path = Path("appserver", "controllers", f"{endpoint_name}.py")
                if not app.file_exists(script_path):
                    yield WarningMessage(
                        "`[{section.name}] is defined, but no corresponding Python script was found.",
                        file_name=filename,
                        line_number=lineno,
                        remediation=f"Create script `{script_path}` or remove the "
                        f"[{section.name}] stanza from {filename}.",
                    )
            elif section.name.startswith("expose:"):
                for key, value in iter(section.options.items()):
                    lineno = config["web"][section.name][key].get_line_number()
                    if key not in ("pattern", "methods"):
                        yield FailMessage(
                            "Only the `pattern` and `methods` properties are permitted for [expose:*] stanzas.",
                            file_name=filename,
                            line_number=lineno,
                            remediation=f"Remove `{key}` from the [{section.name}] stanza.",
                        )
