# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Python file standards
"""
from __future__ import annotations

import ast
import logging
import platform
import re
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any as AnyType
from typing import Generator, Tuple

import semver

import splunk_appinspect
from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.check_routine.python_ast_searcher.ast_searcher import AstSearcher
from splunk_appinspect.check_routine.python_ast_searcher.node_filters import is_sub_class_def
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.python_analyzer import utilities
from splunk_appinspect.python_analyzer.ast_info_query import Any
from splunk_appinspect.python_analyzer.ast_types import AstVariable
from splunk_appinspect.python_modules_metadata.metadata_common import metadata_consts
from splunk_appinspect.python_modules_metadata.python_modules_metadata_store import metadata_store
from splunk_appinspect.regex_matcher import RegexBundle, RegexMatcher

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.python_analyzer.ast_analyzer import AstAnalyzer
    from splunk_appinspect.reporter import Reporter
    from splunk_appinspect.validation_report import ApplicationValidationReport

logger = logging.getLogger(__name__)

report_display_order = 40


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_compiled_python(app: "App", reporter: "Reporter") -> None:
    """Check that there are no `.pyc` or `.pyo` files included in the app."""
    for directory, filename, _ in app.iterate_files(types=[".pyc", ".pyo"]):
        current_file_relative_path = Path(directory, filename)
        reporter_output = f"A Compiled Python file was detected. File: {current_file_relative_path}"
        reporter.fail(reporter_output, current_file_relative_path)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.AST,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_possible_threading(app: "App", reporter: "Reporter") -> None:
    """Check for the use of threading, and multiprocesses. Threading or process must be
    used with discretion and not negatively affect the Splunk installation as a
    whole.
    """
    client = app.python_analyzer_client
    circle_check_namespace = [
        "os.forkpty",
        "os.fork",
        "thread.start_new_thread",
        "os.kill",
        "os.killpg",
        "threading.Thread.start",
        "multiprocessing.Process.start",
    ]
    modules = [
        metadata_consts.ModuleNameConsts.OS,
        metadata_consts.ModuleNameConsts.SUBPROCESS,
        metadata_consts.ModuleNameConsts.THREAD,
        metadata_consts.ModuleNameConsts.THREADING,
        metadata_consts.ModuleNameConsts._THREAD,  # pylint: disable=W0212
        metadata_consts.ModuleNameConsts.MULTIPROCESSING,
    ]
    check_objects = (
        metadata_store.query()
        .namespace_prefixes(modules)
        .tag(metadata_consts.TagConsts.THREAD_SECURITY)
        .python_compatible()
        .collect()
    )
    for file_path, ast_info in client.get_all_ast_infos():
        for check_object in check_objects:
            module_name = ".".join(check_object.namespace.split(".")[:-1])
            # questionable functions in circle invoke
            if check_object.namespace in circle_check_namespace:
                loop_nodes = utilities.find_python_function_in_loop(ast_info, module_name, check_object.name)
                for node in loop_nodes:
                    reporter_output_for_loopcheck = (
                        f"The following line contains questionable usage `{check_object.namespace}` in loop. "
                        "Use threading and multiprocessing with discretion. "
                        f"File: {file_path} "
                        f"Line: {node.lineno}"
                    )
                    reporter.warn(
                        reporter_output_for_loopcheck,
                        file_name=file_path,
                        line_number=node.lineno,
                    )
            else:
                node_linenos = ast_info.get_module_function_call_usage(module_name, check_object.name, lineno_only=True)
                for node_lineno in node_linenos:
                    reporter_output = (
                        f"The following line contains {check_object.namespace} usage. "
                        "Use threading and multiprocessing with discretion. "
                        f"File: {file_path} "
                        f"Line: {node_lineno}"
                    )
                    reporter.warn(
                        reporter_output,
                        file_name=file_path,
                        line_number=node_lineno,
                    )


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.AST,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_python_udp_network_communications(app: "App", reporter: "Reporter") -> None:
    """Check for UDP network communication"""
    reporter_output = (
        "Please check for inbound or outbound UDP network communications. "
        "Any programmatic UDP network communication is prohibited due to security risks in Splunk Cloud and App Certification. "
        "The use or instruction to configure an app using Settings -> Data Inputs -> UDP within Splunk is permitted. Note: "
        "UDP configuration options are not available in Splunk Cloud and as such do not impose a security risk."
    )
    client = app.python_analyzer_client
    for filepath, ast_info in client.get_all_ast_infos():
        # find inner call node usages
        query = ast_info.query().call_nodes(force_propagate=False)
        while not query.is_end():
            query.call_nodes(force_propagate=False)
        udp_nodes = (
            query.filter(Any(ast_info.get_module_function_call_usage("socket", "socket", fuzzy=True)))
            .filter(Any(ast_info.get_module_usage("socket.AF_INET")))
            .filter(Any(ast_info.get_module_usage("socket.SOCK_DGRAM")))
            .collect()
        )
        for node in udp_nodes:
            reporter.fail(reporter_output, filepath, node.lineno)


class CheckAllPythonFilesWellFormed(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_all_python_files_are_well_formed",
                description="Check all python files are well-formed under python3 standard.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.AST,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                    Tags.FUTURE,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    def check(self, app: "App") -> None:
        client = app.python_analyzer_client

        error_template = (
            "Python script is not well formed, {message} when parser tries to parse. "
            "Runtime errors and possible style issues could exist when it is executed."
        )
        error_methods = [
            (client.get_syntax_error_files(), "syntax error found in python script"),
            (client.get_null_byte_error_files(), "python script contains null byte"),
            (client.get_other_exception_files(), "issues like `StackOverFlow` or `SystemError` may exist"),
        ]

        for filepaths, error_message in error_methods:
            for filepath in filepaths:
                yield WarningMessage(
                    error_template.format(message=error_message),
                    file_name=filepath,
                )


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_VICTORIA,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_APP,
    Tags.MIGRATION_VICTORIA,
    Tags.AST,
    Tags.FUTURE,
)
def check_for_custom_python_interpreters(app: "App", reporter: "Reporter") -> None:
    """Check custom python interpreters usage."""
    message = "Usage of `{}` is prohibited due to a possibility of a malicious code execution."

    functions = (
        metadata_store.query()
        .namespace_prefixes([metadata_consts.ModuleNameConsts.CODE])
        .tag(metadata_consts.TagConsts.STRING_EXECUTION)
        .python_compatible()
        .functions()
    )

    files_with_results = AstSearcher(app.python_analyzer_client).search(functions)
    reporter.ast_warn(message, files_with_results)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_VICTORIA,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_APP,
    Tags.MIGRATION_VICTORIA,
    Tags.AST,
    Tags.FUTURE,
)
def check_for_python_multimedia_services(app: "App", reporter: "Reporter") -> None:
    """Check multimedia modules usage."""
    message = (
        "Usage of `{}` to process arbitrary multimedia files is prohibited due to a possibility of malicious content."
    )

    multimedia_modules = [
        metadata_consts.ModuleNameConsts.AIFC,
        metadata_consts.ModuleNameConsts.SUNAU,
        metadata_consts.ModuleNameConsts.WAVE,
        metadata_consts.ModuleNameConsts.CHUNK,
    ]
    query = (
        metadata_store.query()
        .namespace_prefixes(multimedia_modules)
        .tag(metadata_consts.TagConsts.FILE_READ_AND_WRITE)
        .python_compatible()
    )
    components = query.functions() + query.classes()

    files_with_results = AstSearcher(app.python_analyzer_client).search(components)
    reporter.ast_warn(message, files_with_results)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_VICTORIA,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_APP,
    Tags.MIGRATION_VICTORIA,
    Tags.AST,
)
def check_for_optional_operating_system_services(app: "App", reporter: "Reporter") -> None:
    """Check for features that are available on selected operating systems only."""
    objects = (
        metadata_store.query()
        .namespace_prefixes([metadata_consts.ModuleNameConsts.MMAP])
        .tag(metadata_consts.TagConsts.MEMORY_MAPPING)
        .python_compatible()
        .collect()
    )
    message = "Found usage of `{}` which might not work on every operating system."
    files_with_results = AstSearcher(app.python_analyzer_client).search(objects)
    reporter.ast_warn(message, files_with_results)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.AST,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_root_privilege_escalation(app: "App", reporter: "Reporter") -> None:
    """Check possible root privilege escalation"""

    def is_sudo_and_su_usage_exists(call_node: ast.Call, ast_info: "AstAnalyzer") -> bool:
        for arg in call_node.args:
            for ast_node in ast.walk(arg):
                variable = ast_info.get_variable_details(ast_node)
                if AstVariable.is_string(variable):
                    # check exactly match and prefix match
                    if variable.variable_value in ["su", "sudo"]:
                        return True
                    if variable.variable_value.startswith("su ") or variable.variable_value.startswith("sudo "):
                        return True
        return False

    check_objects = (
        metadata_store.query().tag(metadata_consts.TagConsts.EXTERNAL_COMMAND_EXECUTION).python_compatible().collect()
    )
    files_with_results = AstSearcher(app.python_analyzer_client).search(
        check_objects, node_filter=is_sudo_and_su_usage_exists
    )
    reporter.ast_fail("Root privilege escalation detected using {}", files_with_results)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.AST,
    Tags.FUTURE,
)
def check_for_program_frameworks(app: "App", reporter: "Reporter") -> None:
    """Check program frameworks usage."""
    check_objects = (
        metadata_store.query()
        .namespace_prefix(metadata_consts.ModuleNameConsts.CMD)
        .tag(metadata_consts.TagConsts.EXTERNAL_COMMAND_EXECUTION)
        .python_compatible()
        .collect()
    )
    message = "Usage of {}'s derived classes to interface with other parts of the system is prohibited."
    searcher = AstSearcher(app.python_analyzer_client)
    files_with_results = searcher.search(check_objects, node_filter=is_sub_class_def, search_module_usage=True)
    reporter.ast_warn(message, files_with_results)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_CLASSIC,
    Tags.PRIVATE_VICTORIA,
    Tags.PRIVATE_APP,
    Tags.MIGRATION_VICTORIA,
    Tags.AST,
    Tags.FUTURE,
)
def check_for_debugging_and_profiling(app: "App", reporter: "Reporter") -> None:
    """Check debugging libraries usage."""
    check_objects = (
        metadata_store.query()
        .namespace_prefix(metadata_consts.ModuleNameConsts.TRACE)
        .tag(metadata_consts.TagConsts.EXTERNAL_COMMAND_EXECUTION)
        .python_compatible()
        .collect()
    )
    message = "Usage of `{}` to execute arbitrary commands is prohibited."
    files_with_results = AstSearcher(app.python_analyzer_client).search(check_objects)
    reporter.ast_warn(message, files_with_results)


@splunk_appinspect.tags(Tags.SPLUNK_APPINSPECT, Tags.CLOUD)
def check_python_httplib2_version(app: "App", reporter: "Reporter") -> None:
    """Check python httplib2 version."""
    min_ver = semver.VersionInfo.parse("0.19.1")
    ver_rex = r'__version__ = "([\d.]+)"'
    httplib2_exists = False
    py_files = list(app.iterate_files(types=[".py"]))
    # Look for __version__ = "0.18" in httplib2/__init__.py
    rexs = [RegexBundle(ver_rex)]
    matcher = RegexMatcher(rexs)
    if py_files:
        for directory, file, _ in py_files:
            if not (file == "__init__.py" and str(directory).endswith("httplib2")):
                continue
            file_path = Path(directory, file)
            full_file_path = app.get_filename(file_path)
            match_result = matcher.match_file(filepath=full_file_path)
            for lineno, result in match_result:
                httplib2_exists = True
                file_path = Path(directory, file)
                # Parse the found version into semver, correcting for
                # bad versions like "0.1" without a patch version
                try:
                    ver = re.search(ver_rex, result).groups()[0]
                    if len(ver.split(".")) == 2:
                        ver += ".0"  # correct for versions without a patch
                    parsed_ver = semver.VersionInfo.parse(ver)
                except Exception as err:
                    reporter_output = (
                        "Issue parsing version found in for the python httplib2"
                        f" ({ver}). File: {file_path}. Error: {err}."
                    )
                    reporter.warn(reporter_output, file_path)
                    continue

                if parsed_ver < min_ver:
                    # Found httplib2 version is less than the minimum
                    reporter_output = (
                        "Detected an outdated version of the Python httplib2"
                        f" ({ver}). Please upgrade to version "
                        f"{min_ver[0]}.{min_ver[1]}.{min_ver[2]} or later. "
                        f"File: {file_path}."
                    )
                    reporter.warn(reporter_output, file_path)

    # httplib2/__init__.py not found
    if not httplib2_exists:
        reporter_output = "Python httplib2 library not found."
        reporter.not_applicable(reporter_output)


class CheckPythonSdkVersion(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_python_sdk_version",
                description="Check that Splunk SDK for Python is up-to-date.",
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

    MINIMUM_SDK_VERSION = semver.VersionInfo.parse("2.0.2")
    LATEST_SDK_VERSION = semver.VersionInfo.parse("2.1.0")

    VERSION_PATTERN = r"__version_info__\s*=\s*\((.*?)\)"

    @Check.depends_on_matching_files(
        patterns=[r"splunk-sdk-python/(%s|[\d.]+)"],
        names=["binding.py"],
        not_applicable_message="Splunk SDK for Python not found.",
    )
    def check_python_sdk(
        self, app: "App", path_in_app: str, line_number: int, result: "ApplicationValidationReport"
    ) -> Generator[CheckMessage, AnyType, None]:
        # Parse the found version into semver, correcting for
        # bad versions like "0.1" without a patch version
        try:
            path_in_app = Path(path_in_app)
            versions = self._get_raw_sdk_version(app, path_in_app, result, line_number)
        except Exception as err:
            yield WarningMessage(
                f"Issue parsing version found for the Splunk SDK for Python. Error: {err}.",
                file_name=path_in_app,
                line_number=line_number,
            )
            return

        for raw_version, line_number, parsed_ver, path_in_app in versions:
            if parsed_ver < self.MINIMUM_SDK_VERSION:
                # Found splunklib version is less than the minimum
                yield FailMessage(
                    f"Detected an outdated version of the Splunk SDK for Python ({raw_version}).",
                    file_name=path_in_app,
                    line_number=line_number,
                    remediation=f"Upgrade to {self.MINIMUM_SDK_VERSION} or later.",
                )
            elif self.MINIMUM_SDK_VERSION <= parsed_ver < self.LATEST_SDK_VERSION:
                yield WarningMessage(
                    f"Detected an outdated version of the Splunk SDK for Python ({raw_version}).",
                    file_name=path_in_app,
                    line_number=line_number,
                    remediation=f"Upgrade to {self.LATEST_SDK_VERSION} or later.",
                )
            else:
                yield WarningMessage(
                    f"Splunk SDK for Python detected (version {raw_version}).",
                    file_name=path_in_app,
                    line_number=line_number,
                    remediation="No action required at this time.",
                )

    def _parse_version_info(self, raw_version: str) -> semver.VersionInfo:
        return semver.VersionInfo.parse(raw_version)

    def _format_version_info(self, raw_version: str) -> str:
        if len(raw_version.split(".")) == 2:
            raw_version += ".0"
        return raw_version

    def _get_raw_sdk_version(
        self, app: App, path_in_app: Path, result, line_number: int
    ) -> Generator[tuple, None, None]:
        """
        AppInspect fetches SDK version from SDK python files.

        Below 1.7.2 - binding.py -> in line: "User-Agent": "splunk-sdk-python/x.y.z"
        Above - __init__.py -> in line: __version_info__ = (x, y, z)
        """
        base_dir = path_in_app.parent
        raw_version_binding = result.groups()[0]
        line_number_init, raw_version_init, path_in_app_init = self._get_sdk_version(app, base_dir)
        raw_version_init = self._format_version_info(raw_version_init)
        parsed_ver_init = self._parse_version_info(raw_version_init)

        yield (raw_version_init, line_number_init, parsed_ver_init, path_in_app_init)

        if raw_version_binding != "%s":
            raw_version_binding = self._format_version_info(raw_version_binding)
            parsed_ver_binding = self._parse_version_info(raw_version_binding)
            yield (raw_version_binding, line_number, parsed_ver_binding, path_in_app)

    @staticmethod
    def _decode_result(result):
        file_path, match = result[0]
        line_number = file_path.split(":")[1]
        version_raw = match.groups()[0]
        return line_number, version_raw

    def _get_sdk_version(self, app: App, base_dir: Path) -> Tuple:
        """
        Check __init__.py file in splunklib dir
        """
        version_file = "__init__.py"

        result = app.search_for_patterns([self.VERSION_PATTERN], basedir=base_dir, names=[version_file])
        line_number, version_raw = self._decode_result(result)
        version_unified = version_raw.replace(", ", ".")

        file_path = base_dir.joinpath(version_file)

        return line_number, version_unified, file_path


class CheckProhibitedPythonFilenames(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_prohibited_python_filenames",
                description="Check that builtin modules are not overridden.",
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

    @Check.depends_on_files(
        basedir=[Path("bin")],
        names=[
            "builtins.py",
            "copyreg.py",
            "html.py",
            "http.py",
            "queue.py",
            "reprlib.py",
            "socketserver.py",
            "test.py",
            "tkinter.py",
            "winreg.py",
            "xmlrpc.py",
            "_dummy_thread.py",
            "_markupbase.py",
            "_thread.py",
        ],
        recurse_depth=0,
        not_applicable_message="No forbidden python files were found.",
    )
    def check_prohibited_python_filenames(self, app: "App", path_in_app: str) -> Generator[CheckMessage, Any, None]:
        """
        Future automatically imports given modules, and if they are overridden by
        top-level files (in bin/), then they get executed - details:
        https://github.com/PythonCharmers/python-future/blob/master/src/future/standard_library/__init__.py#L799
        """
        yield FailMessage(
            "Found a python file with a name matching a builtin library. "
            "Overriding builtin modules is prohibited. Rename or remove the file.",
            file_name=path_in_app,
        )
