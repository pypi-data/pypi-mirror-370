# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Source code and binaries standards
"""

# TODO: Provide url link to the criteria here in the docstring
from __future__ import annotations

import logging
import os
import platform
import re
import stat
from pathlib import Path
from typing import TYPE_CHECKING

import magic

import splunk_appinspect
import splunk_appinspect.check_routine as check_routine
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.reporter import Reporter


if platform.system() == "Windows":
    import ntsecuritycon as con  # pylint: disable=E0401
    import win32security  # pylint: disable=E0401

logger = logging.getLogger(__name__)
report_display_order = 5


@splunk_appinspect.tags(Tags.SPLUNK_APPINSPECT, Tags.CLOUD, Tags.PRIVATE_APP, Tags.PRIVATE_CLASSIC)
def check_for_bin_files(app: "App", reporter: "Reporter") -> None:
    """Check that files outside the `bin/` and `appserver/controllers` directory do not have execute
    permissions.
    Splunk Cloud is a Linux-based platform, Splunk recommends 644 for all app files outside the `bin/` directory, 644 for
    scripts within the `bin/` directory that are invoked using an interpreter (e.g. `python my_script.py`
    or `sh my_script.sh`), and 755 for scripts within the `bin/` directory that are invoked directly
    (e.g. `./my_script.sh` or `./my_script`).
    """
    directories_to_exclude_from_root = ["bin"]
    for dir, filename, ext in app.iterate_files(excluded_dirs=directories_to_exclude_from_root):
        if dir == Path("appserver", "controllers"):
            continue
        current_file_relative_path = Path(dir, filename)
        current_file_full_path = app.get_filename(current_file_relative_path)
        file_statistics = current_file_full_path.stat()
        # Checks the file's permissions against execute flags to see if the file
        # is executable
        if bool(file_statistics.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)):
            reporter.fail(
                "This file has execute permissions for owners, groups, or others. "
                f"File: {current_file_relative_path}",
                current_file_relative_path,
            )


def _read_windows_file_ace(file_path):
    sd = win32security.GetFileSecurity(str(file_path), win32security.DACL_SECURITY_INFORMATION)
    dacl = sd.GetSecurityDescriptorDacl()
    if dacl is None:
        dacl = _new_dacl_with_all_control()
    # get the number of access control entries
    ace_count = dacl.GetAceCount()
    for i in range(ace_count):
        # rev: a tuple of (AceType, AceFlags)
        # access: ACCESS_MASK
        # usersid: SID
        rev, access, usersid = dacl.GetAce(i)
        user, _, _ = win32security.LookupAccountSid("", usersid)
        ace_type = rev[0]
        yield ace_type, user, access


def _has_permission(access, permission):
    return access & permission == permission


def _new_dacl_with_all_control():
    dacl = win32security.ACL()
    everyone, _, _ = win32security.LookupAccountName("", "Everyone")
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, everyone)
    return dacl


def _get_windows_file_owner(file_path):
    sd = win32security.GetFileSecurity(str(file_path), win32security.OWNER_SECURITY_INFORMATION)
    owner_sid = sd.GetSecurityDescriptorOwner()
    user, _, _ = win32security.LookupAccountSid(None, owner_sid)
    return user
