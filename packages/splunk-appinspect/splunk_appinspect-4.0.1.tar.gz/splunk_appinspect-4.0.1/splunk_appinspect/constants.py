class Tags:
    AARCH_64 = "aarch64_compatibility"
    AST = "ast"
    CLOUD = "cloud"
    FUTURE = "future"
    MIGRATION_VICTORIA = "migration_victoria"
    PACKAGING_STANDARDS = "packaging_standards"
    PRIVATE_APP = "private_app"
    PRIVATE_CLASSIC = "private_classic"
    PRIVATE_VICTORIA = "private_victoria"
    SPLUNK_APPINSPECT = "splunk_appinspect"


PYTHON_3_VERSIONS = ["python3", "python3.7", "python3.9"]
PYTHON_LATEST_VERSION = "latest"
MAX_PACKAGE_SIZE = 2048
SPLUNK_PACKAGING_DOC_URL = (
    "https://dev.splunk.com/enterprise/docs/releaseapps/packageapps/#Third-party-utilities-and-CLI-commands"
)

BUILT_IN_ALERT_ACTIONS = {
    "email",
    "rss",
    "lookup",
    "summary_index",
    "summary_metric_index",
    "populate_lookup",
}
