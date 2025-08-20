# Copyright 2019 Splunk Inc. All rights reserved.

import logging
import os
import re
from pathlib import Path

from . import inspected_file
from .configuration_file import ConfigurationSetting

logger = logging.getLogger(__name__)


class RegexMatcher(object):
    MESSAGE_LIMIT = 80

    def __init__(self, regex_bundle_list):
        self.__regex_bundle_list = regex_bundle_list
        for regex_bundle in self.__regex_bundle_list:
            assert isinstance(regex_bundle, RegexBundle), regex_bundle
        self.has_valid_files = False

    def match(self, string, regex_option=0):
        """return all match results in sorted order"""
        if isinstance(string, ConfigurationSetting):
            string = string.value

        match_list = []
        for regex_bundle in self.__regex_bundle_list:
            pattern = re.compile(regex_bundle.general_regex_string, regex_option)
            result = re.finditer(pattern, string)
            for match_result in result:
                match_list.append(self._get_match_result(regex_bundle, match_result))
        match_list.sort()
        return match_list

    def match_string_array(self, string_array, regex_option=0):
        """return all match results in (lineno, result) tuple and in sorted order"""
        matched = []
        for regex_bundle in self.__regex_bundle_list:
            pattern = re.compile(regex_bundle.general_regex_string, regex_option)
            for index, string in enumerate(string_array):
                result = re.finditer(pattern, string)
                for match_result in result:
                    matched.append((index + 1, self._get_match_result(regex_bundle, match_result)))
        matched.sort()
        return matched

    def match_file(self, filepath, regex_option=0, exclude_comments=True, match_whole_file=False):
        """return all match results in (lineno, result) tuple and in sorted order"""
        if not os.path.exists(filepath):
            return []

        filepath_str = str(filepath)
        file_to_inspect = inspected_file.InspectedFile.factory(filepath)
        result = []
        for regex_bundle in self.__regex_bundle_list:
            pattern = regex_bundle.regex_string(filepath_str)
            if match_whole_file:
                matches = file_to_inspect.search_for_patterns_in_whole_file(pattern, regex_option=regex_option)

                for filename, file_match in matches:
                    result.append(
                        (
                            filename,
                            self._get_match_result(regex_bundle, file_match, filepath_str),
                        )
                    )
            else:
                matches = file_to_inspect.search_for_pattern(
                    pattern, exclude_comments=exclude_comments, regex_option=regex_option
                )

                for fileref_output, file_match in matches:
                    lineno = fileref_output.rsplit(":", 1)[1]
                    result.append(
                        (
                            int(lineno),
                            self._get_match_result(regex_bundle, file_match, filepath_str),
                        )
                    )

        result.sort()
        return result

    def match_results_iterator(
        self, app_dir, file_iterator, regex_option=0, exclude_comments=True, match_whole_file=False
    ):
        directory = _empty = object()
        for directory, filename, _ in file_iterator:
            absolute_path = Path(app_dir, directory, filename)
            file_path = Path(directory, filename)
            match_result = self.match_file(
                filepath=absolute_path,
                regex_option=regex_option,
                exclude_comments=exclude_comments,
                match_whole_file=match_whole_file,
            )
            result_dict = {}
            # dedup result in one line
            for lineno, result in match_result:
                if lineno not in result_dict:
                    result_dict[lineno] = set()
                result_dict[lineno].add(result)
            for lineno, result_set in result_dict.items():
                for result in result_set:
                    # yield result, file_path, lineno
                    yield result, file_path, lineno

        if directory != _empty:
            self.has_valid_files = True

    def _get_match_result(self, regex_bundle, match_result, filepath: str = None):
        raw_result = match_result.group(0)
        if filepath is not None and not regex_bundle.check_if_result_truncated(filepath):
            return raw_result
        if len(raw_result) <= self.MESSAGE_LIMIT:
            return raw_result

        # concatenate subgroups together
        result = "...".join(filter(lambda group: len(group) <= self.MESSAGE_LIMIT, match_result.groups()))
        # subgroups are defined in regex
        if result != "":
            result = "..." + result + "..."
        else:
            result = raw_result[0 : self.MESSAGE_LIMIT] + "..."
        return result


class JSSplunkJSMatcher(RegexMatcher):
    def __init__(self):
        possible_splunkjs_regex_patterns = [RegexBundle(r"splunkjs\/mvc")]
        super(JSSplunkJSMatcher, self).__init__(possible_splunkjs_regex_patterns)


class JSSplunkSUIMatcher(RegexMatcher):
    def __init__(self):
        possible_splunkreactui_regex_patterns = [
            RegexBundle(
                r"@splunk\/(react-ui|react-search|react-time-range|react-page|react-icons|themes|react-toast-notifications)"
            )
        ]
        super(JSSplunkSUIMatcher, self).__init__(possible_splunkreactui_regex_patterns)


# Check for Utility Components Listed on this site:
class JSSplunkSplunkFrontendUtils(RegexMatcher):
    def __init__(self):
        possible_splunkutils_regex_patterns = [RegexBundle(r"@splunk\/(moment|splunk-utils|ui-utils|search-job)")]
        super(JSSplunkSplunkFrontendUtils, self).__init__(possible_splunkutils_regex_patterns)


class JSSplunkDashboardCoreMatcher(RegexMatcher):
    def __init__(self):
        possible_splunkdashboardcore_regex_patterns = [
            RegexBundle(r"@splunk\/(dashboard|datasource)(s)?(-\w+)?(-\w+)?")
        ]
        super(JSSplunkDashboardCoreMatcher, self).__init__(possible_splunkdashboardcore_regex_patterns)


class JSSplunkVisualizationsMatcher(RegexMatcher):
    def __init__(self):
        possible_splunkvisualizations_regex_patterns = [RegexBundle(r"@splunk\/visualization(s)?(-\w+)?")]
        super(JSSplunkVisualizationsMatcher, self).__init__(possible_splunkvisualizations_regex_patterns)


class JSWeakEncryptionMatcher(RegexMatcher):
    def __init__(self):
        weak_encryption_regex_patterns = [RegexBundle(r"CryptoJS\s*\.\s*(DES\s*\.\s*encrypt|MD5|SHA1)")]
        super(JSWeakEncryptionMatcher, self).__init__(weak_encryption_regex_patterns)


class JSReflectedXSSMatcher(RegexMatcher):
    def __init__(self):
        reflected_xss_regex_patterns = [
            RegexBundle(r"<img[ ]+(dynsrc|lowsrc|src)\s*=\s*[\"\' ]javascript:(?!false)[^0].*?>"),
            RegexBundle(r"<(bgsound|iframe|frame)[ ]+src\s*=\s*[\"\' ]javascript:(?!false)[^0].*?>"),
            RegexBundle(r"<a\s*(on.*)\s*=.*?>"),
            RegexBundle(r'<img """><script>.*?</script>">'),
            RegexBundle(r"<img[ ]+(on.*?)\s*=.*?>"),
            RegexBundle(r"<(img|iframe)[ ]+src\s*=\s*#\s*(on.*)\s*=.*?>"),
            RegexBundle(r"<img[ ]+src\s*=\s*(on.*)\s*=.*?>"),
            RegexBundle(r"<img[ ]+src\s*=\s*/\s*onerror\s*=.*?>"),
            RegexBundle(r"<input[ ]+type\s*=\s*[\"\']image[\"\']\s*src\s*=\s*[\"\']javascript:(?!false)[^0].*?>"),
            RegexBundle(r"<(body|table|td)[ ]+background\s*=\s*[\"\']javascript:(?!false)[^0].*?>"),
            RegexBundle(r"<svg[ ]+onload\s*=.*?>"),
            RegexBundle(r"<body\s*ONLOAD\s*=.*?>"),
            RegexBundle(r"<br[ ]+size\s*=\s*[\"\']&\{.*?\}[\"\']>"),
            RegexBundle(r"<link[ ]+href\s*=\s*[\"\']javascript:(?!false)[^0].*?>"),
            RegexBundle(r"<div\s*style\s*=\s*[\"\']background-image:\s*url\(javascript:(?!false)[^0].*?>"),
        ]
        super(JSReflectedXSSMatcher, self).__init__(reflected_xss_regex_patterns)


class ConfEndpointMatcher(RegexMatcher):
    def __init__(self):
        conf_endpoint_regex_patterns = [
            RegexBundle(r"servicesNS/\S*configs/\S*conf-\S*/\S*"),
            RegexBundle(r"services/configs/conf-\S*/\S*"),
            RegexBundle(r"services/properties/\S*/\S*"),
        ]
        super(ConfEndpointMatcher, self).__init__(conf_endpoint_regex_patterns)


class JSTelemetryEndpointMatcher(RegexMatcher):
    def __init__(self):
        possible_telemetry_endpoint_regex_patterns = [
            # https://<host>:<management_port>/servicesNS/<user_context>/<app_context>/telemetry-metric
            RegexBundle(r"(?:https|http)://\S*/servicesNS/\S*/telemetry-metric"),
            # http://<host>:<splunkweb_port>/<locale>/splunkd/__raw/servicesNS/<user_context>/<app_context>/telemetry-metric
            RegexBundle(r"(?:https|http)://\S*/splunkd/__raw/servicesNS/\S*/telemetry-metric"),
        ]
        super(JSTelemetryEndpointMatcher, self).__init__(possible_telemetry_endpoint_regex_patterns)


class JSTelemetryMetricsMatcher(RegexMatcher):
    def __init__(self):
        telemetry_regex_patterns = [
            RegexBundle(r"window\._splunk_metrics_events\.push\s*"),
            RegexBundle(r"(splunk_metrics|\w+)\.trackEvent\s*"),
            RegexBundle(r"(splunk_metrics|\w+)\.init\([^}]*logging.*true\)"),
            RegexBundle(r"(splunk_metrics|\w+)\.init\([^}]*log.*\)"),
        ]
        super(JSTelemetryMetricsMatcher, self).__init__(telemetry_regex_patterns)


class RegexBundle(object):
    def __init__(self, regex_string: str):
        self._regex_string = regex_string
        self._exception_dict = {}

    @property
    def general_regex_string(self):
        return self._regex_string

    def exception(self, filepath: str, regex_string: str, is_truncated: bool = True):
        self._exception_dict[filepath] = (regex_string, is_truncated)

    def regex_string(self, filepath: str):
        for suffix, (regex_string, _) in self._exception_dict.items():
            if filepath.endswith(suffix):
                return regex_string
        return self._regex_string

    def check_if_result_truncated(self, filepath: str):
        for suffix, (_, is_truncated) in self._exception_dict.items():
            if filepath.endswith(suffix):
                return is_truncated
        return True
