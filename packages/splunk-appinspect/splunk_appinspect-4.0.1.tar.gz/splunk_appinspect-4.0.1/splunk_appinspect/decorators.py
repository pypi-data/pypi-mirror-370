# Copyright 2019 Splunk Inc. All rights reserved.

"""Each of these add metadata to the function they wrap. This metadata is then
used by the Check object that encloses it.
"""
from typing import Callable


def tags(*args: str) -> Callable:
    """Allows specifying of different groups of checks via tags."""

    def wrap(check: Callable) -> Callable:
        check.tags = args
        return check

    return wrap


def display(report_display_order: int = 1000) -> Callable:
    """Allows specifying an order for checks to appear within a group."""

    def wrap(check: Callable) -> Callable:
        check.report_display_order = report_display_order
        return check

    return wrap
