"""App Utilities API"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Union

import semver

from splunk_appinspect.regex_matcher import RegexBundle, RegexMatcher

if TYPE_CHECKING:
    from splunk_appinspect.app import App


def _is_path_outside_app_container(path: str, app_name: str, is_windows: bool) -> bool:
    environs = ["$SPLUNK_HOME"]
    if is_windows:
        environs.append("%SPLUNK_HOME%")

    for environ in environs:
        if path.startswith(environ):
            app_container = Path(environ, "etc", "apps", app_name)
            # FIXME: change to is_relative_to(app_container) after upgrading to python 3.9
            if not path.startswith(str(app_container)):
                return True
            return False
    return True


def is_manipulation_outside_of_app_container(path: Union[str, Path], app_name: str) -> bool:
    path = str(path)
    if len(path) >= 2 and path[0] in ["'", '"']:
        if path[0] == path[-1]:
            path = path[1:-1]
        else:
            # TODO MALFORMED?
            pass
    if path.count(os.sep) > 0 or path.count("/"):
        if path.startswith(os.sep) or path.startswith("/"):
            return True

        np = os.path.normpath(path)
        # On Windows, splunk can recognize $SPLUNK_HOME and %SPLUNK_HOME%
        if os.name == "nt":
            if re.match(r"([a-zA-Z]\:|\.)\\", np):
                return True
            return _is_path_outside_app_container(np, app_name, True)

        return _is_path_outside_app_container(np, app_name, False)

    if path.startswith(".."):
        return True
    return False


class AppVersionNumberMatcher(RegexMatcher):
    """Splunk App Version Matcher"""

    def __init__(self):
        version_number_regex_patterns = [
            # ex) match 2.10.dev
            RegexBundle(r"^(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<others>[\w\-\+]*)$"),
            # ex) match 2.10.1dev
            RegexBundle(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<revision>\d+)(?P<suffix>[0-9a-z\-\+]*)$"),
            # ex) match 2.10.1-dev+bundle
            RegexBundle(semver.VersionInfo._REGEX.pattern.replace(" ", "").replace("\n", "")),
        ]
        super().__init__(version_number_regex_patterns)


def find_readmes(app: App) -> list[str]:
    """Helper function to find all the readmes of a Splunk App"""
    # This is surprisingly complex- an app may have a README file that's
    # documentation. It may also have a README directory that contains
    # conf files.  We could potentially also have multiple readme files,
    # for example for different languages, installation, etc.

    # Heuristic: find all plain files in the root directory that
    # match start with "readme", case-insensitive
    candidates = [Path(f.name) for f in app.app_dir.iterdir() if os.path.isfile(f) and re.match(r"(?i)^readme", f.name)]
    return candidates


def is_relative_to(path: Path, base: Path) -> bool:
    """
    Check if the given path is relative to the base path.
    This is a compatibility function for Python < 3.9.
    TODO Python 3.7: After Python 3.7 gets deprecated, we can use `path.is_relative_to(base)` directly.
    """
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
