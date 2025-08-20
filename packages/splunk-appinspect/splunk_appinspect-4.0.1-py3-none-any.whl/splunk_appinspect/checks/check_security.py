# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Security vulnerabilities
"""
from __future__ import annotations

import ast
import logging
import os
import platform
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage
from splunk_appinspect.check_routine.python_ast_searcher.ast_searcher import AstSearcher
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.file_resource import FileResource
from splunk_appinspect.python_analyzer.ast_types import AstVariable
from splunk_appinspect.python_modules_metadata.metadata_common import metadata_consts
from splunk_appinspect.python_modules_metadata.python_modules_metadata_store import metadata_store

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.python_analyzer.ast_analyzer import AstAnalyzer
    from splunk_appinspect.reporter import Reporter


logger = logging.getLogger(__name__)
report_display_order = 5


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_sensitive_info_in_url(app: "App", reporter: "Reporter") -> None:
    """Check for sensitive information being exposed in transit via URL query string parameters"""
    sensitive_info_patterns = re.compile(
        r"([ \f\r\t\v]*[0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*[\"\']?https?://[^\"\'\s]*?(key|pass|pwd|token)[0-9a-z]*=[^&\"\'\s]+[\"\']?|"  # Single line url
        r"[ \f\r\t\v]*[0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*([\"\']\{\}://\{\}:\{\}@\{\}:\{\}[\"\'])\.format\([^\)]*(key|password|pass|pwd|token|cridential|secret|login|auth)[^\)]*\))",
        re.IGNORECASE,
    )  # Multi line url

    sensitive_info_patterns_for_report = re.compile(
        r"([0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*[\"\']?https?://[^\"\'\s]*?(key|pass|pwd|token)[0-9a-z]*=[^&\"\'\s]+[\"\']?|"  # Single line url
        r"[0-9a-z_\.]*(url|uri|host|server|prox|proxy_str)s?[ \f\r\t\v]*=[ \f\r\t\v]*([\"\']\{\}://\{\}:\{\}@\{\}:\{\}[\"\'])\.format\([^\)]*(key|password|pass|pwd|token|cridential|secret|login|auth)[^\)]*\))",
        re.IGNORECASE,
    )  # Multi line url

    for match in app.search_for_crossline_pattern(pattern=sensitive_info_patterns, cross_line=5):
        filename, line = match[0].rsplit(":", 1)
        # handle massage
        for rx in [re.compile(p) for p in [sensitive_info_patterns_for_report]]:
            for p_match in rx.finditer(match[1].group()):
                description = p_match.group()
                reporter_output = (
                    f"Possible sensitive information being exposed via URL in {match[0]}: {description}."
                    f" File: {filename}, Line: {line}."
                )
                reporter.warn(reporter_output, filename, line)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_VICTORIA,
    Tags.AST,
    Tags.MIGRATION_VICTORIA,
)
def check_for_insecure_http_calls_in_python(app: "App", reporter: "Reporter") -> None:
    """Check for insecure HTTP calls in Python."""
    report_template = "Insecure HTTP Connection found" " Match: {}" " Positional arguments, {}; Keyword arguments, {}"

    query = metadata_store.query().tag(metadata_consts.TagConsts.HTTP_CONNECTION).python_compatible()

    def is_not_secure_var(var, ast_info: "AstAnalyzer") -> bool:
        variable = ast_info.get_variable_details(var)
        return AstVariable.is_string(variable) and not variable.variable_value.startswith("https")

    def is_arg_not_secure(call_node: ast.Call, ast_info: "AstAnalyzer") -> bool:
        # check if https prefix is found
        is_not_secure = False
        # only pay attention to first two arguments, url will always be included
        for arg in call_node.args[:2]:
            is_not_secure = is_not_secure_var(arg, ast_info)
            if is_not_secure:
                break
        return is_not_secure

    def is_keyword_not_secure(call_node: ast.Call, ast_info: "AstAnalyzer") -> bool:
        is_not_secure = False
        possible_argument_keys = {"url", "fullurl", "host"}
        for keyword in call_node.keywords:
            if keyword.arg in possible_argument_keys:
                is_not_secure = is_not_secure_var(keyword.value, ast_info)
                if is_not_secure:
                    break
        return is_not_secure

    def is_arg_secure_or_keyword_secure(call_node: ast.Call, ast_info: "AstAnalyzer") -> bool:
        return is_arg_not_secure(call_node, ast_info) or is_keyword_not_secure(call_node, ast_info)

    components = query.functions() + query.classes()
    if len(components) > 0:
        files_with_results = AstSearcher(app.python_analyzer_client).search(
            components, node_filter=is_arg_secure_or_keyword_secure, get_func_params=True
        )
        reporter.ast_warn(report_template, files_with_results)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_symlink_outside_app(app: "App", reporter: "Reporter") -> None:
    """Check no symlink points to the file outside this app"""
    if platform.system() == "Windows":
        reporter_output = "Please run AppInspect using another OS to enable this check. Or use AppInspect API."
        reporter.warn(reporter_output)
    else:
        for basedir, file, _ in app.iterate_files():
            app_file_path = Path(basedir, file)
            full_file_path = app.get_filename(app_file_path)
            # it is a symbolic link file
            if os.path.islink(full_file_path):
                # For python 2.x, os.path.islink will always return False in windows
                # both of them are absolute paths
                link_to_absolute_path = os.path.abspath(Path(full_file_path).resolve())
                # link to outer path
                # FIXME: change to is_relative_to(app_root_dir) after upgrading to python 3.9
                if not link_to_absolute_path.startswith(str(app.app_dir)):
                    reporter_output = (
                        f"Link file found in path: {full_file_path}. The file links to a path "
                        f"outside of this app, the link path is: {link_to_absolute_path}."
                    )
                    reporter.fail(reporter_output, app_file_path)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
    Tags.CLOUD,
    Tags.AST,
    Tags.FUTURE,
)
def check_for_supported_tls(app: "App", reporter: "Reporter") -> None:
    """Check that all outgoing connections use TLS in accordance to Splunk Cloud Platform policy."""
    client = app.python_analyzer_client
    internals_addresses = ["localhost", "127.0.0.1", "::1"]
    protocols = ["http://", "https://"]
    allowed_urls = [protocol + internal_address for protocol in protocols for internal_address in internals_addresses]
    allowed_urls = allowed_urls + internals_addresses
    allowed_urls = tuple(allowed_urls)

    def _report_if_all_kwrgs_found(
        ast_info: "AstAnalyzer",
        file_path: Path,
        reporter: "Reporter",
        lib_name: str,
        url_param_index: int,
        url_param_key: str,
        check_kwrgs: dict[str, Any],
    ) -> None:
        usages = ast_info.get_module_function_call_usage(lib_name, fuzzy=True)
        for usage in usages:
            is_local = False
            find_count = 0
            variable_count = 0
            is_url_variable = False
            if hasattr(usage, "keywords"):
                for keyword in usage.keywords:
                    raw_value, has_raw_value = (
                        _extract_raw_string_value(keyword.value) if hasattr(keyword, "value") else (None, False)
                    )
                    if hasattr(keyword, "arg") and has_raw_value:
                        for k, v in check_kwrgs.items():
                            if keyword.arg == k and raw_value == v:
                                find_count = find_count + 1
                        if (
                            keyword.arg == url_param_key
                            and raw_value
                            and (isinstance(raw_value, ast.Constant) or isinstance(raw_value, str))
                            and raw_value.startswith(allowed_urls)
                        ):
                            is_local = True
                    elif hasattr(keyword, "arg"):
                        for k, v in check_kwrgs.items():
                            if keyword.arg == k:
                                variable_count = variable_count + 1
                        if keyword.arg == url_param_key:
                            is_url_variable = True

            if hasattr(usage, "args") and len(usage.args) >= url_param_index + 1:
                raw_value, has_raw_value = _extract_raw_string_value(usage.args[url_param_index])
                if (
                    has_raw_value
                    and raw_value
                    and (isinstance(raw_value, ast.Constant) or isinstance(raw_value, str))
                    and raw_value.startswith(allowed_urls)
                ):
                    is_local = True
                elif not has_raw_value:
                    is_url_variable = True

            if (find_count == len(check_kwrgs) and variable_count == 0) and (not is_local and not is_url_variable):
                reporter_output = "The SSL certificate validation is disabled. Enable the SSL certificate validation for communications with outside the Splunk Cloud stack. This can be done by specifying the relevant parameters (verify, cafile etc) to True or the certificate path."
                if lib_name == "httplib2.Http":
                    reporter.not_applicable(
                        reporter_output, file_path, usage.lineno
                    )  # NOTE - enforcement - change to warning
                else:
                    reporter.warn(reporter_output, file_path, usage.lineno)  # NOTE - enforcement - change to failure
            elif (is_local and not is_url_variable) or (find_count != len(check_kwrgs) and variable_count == 0):
                continue
            else:
                reporter_output = "Ensure that the SSL certificate validation for communications with outside the Splunk Cloud stack is enabled. This can be done by specifying the relevant parameters (verify, cafile etc) to True or the certificate path."
                reporter.not_applicable(
                    reporter_output, file_path, usage.lineno
                )  # NOTE - enforcement - change to warning

    for file_path, ast_info in client.get_all_ast_infos():
        if file_path.suffix == ".py":
            _report_if_all_kwrgs_found(
                ast_info,
                file_path,
                reporter,
                "http.client.HTTPSConnection",
                0,
                "host",
                {"cert_file": None},
            )
            _report_if_all_kwrgs_found(
                ast_info,
                file_path,
                reporter,
                "urllib.request.urlopen",
                0,
                "url",
                {
                    "cafile": None,
                    "capath": None,
                },
            )
            _report_if_all_kwrgs_found(
                ast_info,
                file_path,
                reporter,
                "httplib2.Http",
                0,
                "uri",
                {"disable_ssl_certificate_validation": True},
            )
            for request_method in (
                "requests.request",
                "requests.get",
                "requests.post",
                "requests.patch",
                "requests.put",
            ):
                param_index = 0
                if request_method == "requests.request":
                    param_index = 1
                _report_if_all_kwrgs_found(
                    ast_info, file_path, reporter, request_method, param_index, "url", {"verify": False}
                )


def _extract_raw_string_value(arg) -> (str, bool):
    # ast.Str was used instead of ast.Constant in python3.7 (https://github.com/python/cpython/issues/77073), which did not have property 'value'
    if hasattr(arg, "value"):
        return arg.value, True
    if isinstance(arg, ast.Str):
        return arg.s, True
    return None, False


class CheckForCamelJars(Check):
    AFFECTED_PACKAGES_NAMES = {
        "camel",
        "camel-activemq",
        "camel-activemq6",
        "camel-amqp",
        "camel-aws2-sqs",
        "camel-azure-servicebus",
        "camel-bean",
        "camel-cxf-rest",
        "camel-cxf-soap",
        "camel-http",
        "camel-jetty",
        "camel-jms",
        "camel-kafka",
        "camel-knative",
        "camel-mail",
        "camel-nats",
        "camel-netty-http",
        "camel-platform-http",
        "camel-rest",
        "camel-servlet",
        "camel-sjms",
        "camel-spring-rabbitmq",
        "camel-stomp",
        "camel-tahu",
        "camel-undertow",
        "camel-xmpp",
    }

    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_for_camel_jars",
                description="Check for vulnerable Apache Camel dependencies.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    @staticmethod
    def _is_affected_version(version: str) -> bool:
        """
        affected versions:
        from 4.10.0 before 4.10.2
        from 4.8.0 before 4.8.5
        from 3.10.0 before 3.22.4
        """
        versions = {"4.10.0", "4.10.1", "4.8.0", "4.8.1", "4.8.2", "4.8.3", "4.8.4"}

        if version.startswith("4") and version in versions:
            return True
        elif version.startswith("3"):
            _, minor, patch = [int(x) for x in version.split(".")]
            if 10 <= minor <= 21 or (minor == 22 and patch < 4):
                return True

        return False

    def _is_affected_package(self, package: str, version: str) -> bool:
        if package in self.AFFECTED_PACKAGES_NAMES and self._is_affected_version(version):
            return True

        return False

    def _parse_build_gradle(self, filepath: Path, path_in_app: str):
        with open(filepath) as file:
            for line in file:
                # patterns for:
                # 1. "org.apache.camel:<package>:<version>"
                # 2. "group: 'org.apache.camel', name: '<package>', version: '<version>'"
                match = re.search(r"org.apache.camel:([^:]+):([\d\.]+)", line) or re.search(
                    r"group: 'org.apache.camel', name: '([^:]+)', version: '([\d\.]+)'", line
                )
                if match:
                    package_name, version = match.groups()
                    if self._is_affected_package(package_name, version):
                        yield FailMessage(
                            f"A vulnerable dependency found: org.apache.camel:{package_name}:{version}. "
                            f"This artifact is exposed to Camel message header injection via improper "
                            f"filtering. For more information, see CVE-2025-27636.",
                            file_name=path_in_app,
                        )

    def _parse_pom_xml(self, filepath: Path, path_in_app: str):
        file_resource = FileResource(filepath)
        content = file_resource.parse(fmt="xml")
        for dependency in content.find_all("dependency"):
            group_id = dependency.find("groupid").text
            if group_id == "org.apache.camel":
                package_name = dependency.find("artifactid")
                version = dependency.find("version")

                if package_name and version and self._is_affected_package(package_name.text, version.text):
                    yield FailMessage(
                        f"A vulnerable dependency found: org.apache.camel:{package_name}:{version}. "
                        f"This artifact is exposed to Camel message header injection via improper "
                        f"filtering. For more information, see CVE-2025-27636.",
                        file_name=path_in_app,
                    )

    @Check.depends_on_files(
        names=["pom.xml", "build.gradle", "build.gradle.kts"],
        not_applicable_message="No pom.xml, build.gradle or build.gradle.kts file found",
    )
    def check_for_camel_jars(self, app: "App", path_in_app: str) -> Generator[CheckMessage, Any, None]:
        filepath = app.get_filename(path_in_app)

        if filepath.name == "pom.xml":
            yield from self._parse_pom_xml(filepath, path_in_app)

        else:
            yield from self._parse_build_gradle(filepath, path_in_app)
