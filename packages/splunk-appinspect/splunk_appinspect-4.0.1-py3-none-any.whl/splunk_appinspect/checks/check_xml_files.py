# Copyright 2019 Splunk Inc. All rights reserved.

"""
### XML file standards
"""

import logging
import re
import warnings
import xml
from pathlib import Path
from typing import TYPE_CHECKING

import bs4
from defusedxml.sax import make_parser

import splunk_appinspect
from splunk_appinspect.common.xml_utils import ignore_XMLParsedAsHTMLWarning
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.reporter import Reporter


logger = logging.getLogger(__name__)
report_display_order = 7


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_that_all_xml_files_are_well_formed(app: "App", reporter: "Reporter") -> None:
    """Check that all XML files are well-formed."""

    # From Python cookbook
    # https://www.safaribooksonline.com/library/view/python-cookbook-2nd/0596007973/ch12s02.html
    def parse_xml(filename: Path) -> None:
        parser = make_parser()
        parser.parse(str(filename))

    for relative_filepath, full_filepath in app.get_filepaths_of_files(types=[".xml"]):
        try:
            parse_xml(full_filepath)
        except (xml.sax.SAXException, ValueError):
            reporter.fail(f"Invalid XML file: {relative_filepath}", relative_filepath)
