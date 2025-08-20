# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Saved search standards

Saved searches are defined in a **savedsearches.conf** file located in the **/default** and **/local** directory of the app. For more, see [Save and share your reports](https://docs.splunk.com/Documentation/Splunk/latest/SearchTutorial/Aboutsavingandsharingreports) and [savedsearches.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Savedsearchesconf).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generator

from splunk_appinspect.check_messages import (
    CheckMessage,
    FailMessage,
    NotApplicableMessage,
    SkipMessage,
    WarningMessage,
)
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.cron_expression import CronExpression
from splunk_appinspect.saved_searches import SavedSearch
from splunk_appinspect.splunk import normalizeBoolean

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy, ConfigurationSection


report_display_order = 13
logger = logging.getLogger(__name__)


class CheckForRealTimeSavedSearchesForCloud(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_real_time_saved_searches_for_cloud",
                description="Check that no real-time pre-index saved searches are being used in"
                "`savedsearches.conf`. Real-time pre-index saved searches are extremely"
                "system intensive and should be avoided.",
                depends_on_config=("savedsearches",),
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
        # http://docs.splunk.com/Documentation/Splunk/latest/Search/Specifyrealtimewindowsinyoursearch
        saved_searches = app.get_saved_searches(config)
        for search in saved_searches.searches():
            if search.is_real_time_search() and search.enable_sched and not search.is_disabled:
                yield FailMessage(
                    f"The stanza [{search.name}] contains a scheduled real-time"
                    " search, which can have an impact on performance in high volume"
                    " environments and network load. Please disable this search.",
                    file_name=config["savedsearches"].get_relative_path(),
                    line_number=config["savedsearches"][search.name].get_line_number(),
                )

            elif search.is_real_time_search():
                # https://docs.splunk.com/Documentation/Splunk/latest/Search/Realtimeperformanceandlimitations
                yield WarningMessage(
                    f"The stanza [{search.name}] contains a real-time"
                    " search, which might have impact on performance in"
                    " high volume environments and network load.",
                    file_name=config["savedsearches"].get_relative_path(),
                    line_number=config["savedsearches"][search.name].get_line_number(),
                )


class CheckForGratuitousCronScheduling(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_gratuitous_cron_scheduling",
                description="check that `savedsearches.conf` searches are cron scheduled"
                "reasonably. Less than five asterisks should be used.",
                depends_on_config=("savedsearches",),
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
        saved_searches = app.get_saved_searches(config)
        cron_schedule_saved_search = [
            saved_search for saved_search in saved_searches.searches() if saved_search.cron_schedule
        ]

        invalid_cron_schedule_saved_searches = []
        gratuitous_cron_schedule_saved_searches = []
        for saved_search in cron_schedule_saved_search:
            try:
                exp = CronExpression(saved_search.cron_schedule)
                if not exp.is_valid():
                    invalid_cron_schedule_saved_searches.append(saved_search)
                elif exp.is_high_occurring():
                    minutes_field = exp.fields[0]
                    occurrences = CronExpression.get_occurrences_in_an_hour(minutes_field)
                    gratuitous_cron_schedule_saved_searches.append((saved_search, occurrences))
            except ValueError:
                invalid_cron_schedule_saved_searches.append(saved_search)

        if cron_schedule_saved_search:
            if gratuitous_cron_schedule_saved_searches:
                for (
                    saved_search,
                    occurrences,
                ) in gratuitous_cron_schedule_saved_searches:
                    yield WarningMessage(
                        f"The saved search [{saved_search.name}] was detected with"
                        " a high-occurring cron_schedule, i.e. During a period of an hour,"
                        " if the search is scheduled for over 12 times, it will be considered as high"
                        f" occurring. It occurs {occurrences.count(True)} times within 1 hour here."
                        f" Please evaluate whether `cron_schedule = {saved_search.cron_schedule}`"
                        " is appropriate.",
                        file_name=config["savedsearches"].get_relative_path(),
                        line_number=saved_search.args["cron_schedule"].get_line_number(),
                    )
            if invalid_cron_schedule_saved_searches:
                for saved_search in invalid_cron_schedule_saved_searches:
                    yield FailMessage(
                        f"The saved search [{saved_search.name}] was detected with an invalid"
                        " cron_schedule. Please evaluate whether `cron_schedule ="
                        f" {saved_search.cron_schedule}` is valid.",
                        file_name=config["savedsearches"].get_relative_path(),
                        line_number=saved_search.args["cron_schedule"].get_line_number(),
                    )
        else:
            yield NotApplicableMessage("No saved searches with a cron schedule were detected.")


class CheckForSchedSavedSearchesEarliestTime(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_sched_saved_searches_earliest_time",
                description="Check that if a scheduled saved search in savedsearch.conf contains dispatch."
                "earliest_time option, or if a scheduled saved search with auto summary enabled"
                " contains auto_summarize.dispatch.earliest_time option",
                depends_on_config=("savedsearches",),
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

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for section in config["savedsearches"].sections():
            if not section.has_option("search"):
                yield SkipMessage(
                    f"{section.name} does not have a search setting",
                    file_name=section.get_relative_path(),
                    line_number=section.get_line_number(),
                )
            else:
                search_query = section.get_option("search").value

                is_generating_command_search = section.has_option("search") and search_query.strip().startswith("|")
                if is_generating_command_search:
                    # The saved search is based on a generating command which will
                    # create events in real-time so earliest_time isn't needed
                    continue
                if (
                    _is_scheduled_search(section)
                    and not section.has_option("dispatch.earliest_time")
                    and not _is_summary_search_with_earliest_time(section)
                    and not _is_earliest_time_in_query(search_query)
                ):
                    yield FailMessage(
                        f"The saved search [{section.name}] doesn't contain dispatch.earliest_time."
                        "It is prohibited to specify scheduled searches that don't specify a"
                        " dispatch.earliest_time in Splunk Cloud.",
                        file_name=config["savedsearches"].get_relative_path(),
                        line_number=config["savedsearches"][section.name].get_line_number(),
                    )


def _is_scheduled_search(section: "ConfigurationSection") -> bool:
    return section.has_option("enableSched") and normalizeBoolean(section.get_option("enableSched").value.strip())


def _is_summary_search_with_earliest_time(section: "ConfigurationSection") -> bool:
    return (
        section.has_option("auto_summarize")
        and normalizeBoolean(section.get_option("auto_summarize").value.strip())
        and section.has_option("auto_summarize.dispatch.earliest_time")
    )


def _is_earliest_time_in_query(query: str) -> bool:
    earliest_time_keywords = ["earliest", "_index_earliest"]
    for earliest_time_keyword in earliest_time_keywords:
        if earliest_time_keyword in query:
            return True
    return False


class CheckForSchedSavedSearchesLatestTime(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_sched_saved_searches_latest_time",
                description="Check that if a savedsearch.conf stanza contains scheduling options"
                "it does contain a dispatch.latest_time",
                depends_on_config=("savedsearches",),
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

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for section in config["savedsearches"].sections():
            is_generating_command_search = section.has_option("search") and section.get_option(
                "search"
            ).value.strip().startswith("|")
            if is_generating_command_search:
                # The saved search is based on a generating command which will
                # create events in real-time so earliest_time isn't needed
                continue
            if section.has_option("enableSched") and normalizeBoolean(section.get_option("enableSched").value.strip()):
                if section.has_option("dispatch.latest_time"):
                    continue
                yield WarningMessage(
                    f"The saved search [{section.name}] doesn't contain dispatch.latest_time."
                    "It is better to add a dispatch.latest_time when specifying scheduled"
                    " searches in Splunk Cloud. ",
                    file_name=config["savedsearches"].get_relative_path(),
                    line_number=section.get_line_number(),
                )


class CheckForSchedSavedSearchesActionScriptFilename(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_sched_saved_searches_action_script_filename",
                description="Check that savedsearch.conf stanzas do not contain action.script.filename option",
                depends_on_config=("savedsearches",),
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

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for section in config["savedsearches"].sections():
            if section.has_option("action.script.filename"):
                yield FailMessage(
                    f"The saved search [{section.name}] contains action.script.filename. which is not allowed in Splunk Cloud."
                    "Create a custom alert action instead of a custom script.",
                    file_name=config["savedsearches"].get_relative_path(),
                    line_number=section.get_line_number(),
                )


class CheckForSchedSavedSearchesPopulateLookup(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_saved_searches_populate_lookup",
                description="Check that savedsearch.conf stanza do not contain action.populate_lookup option`.",
                depends_on_config=("savedsearches",),
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

    POPULATE_LOOKUP_ALLOW_VALUES = ["0", "disabled", "false"]
    POPULATE_LOOKUP_OPTION_KEY = "action.populate_lookup"

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        for section in config["savedsearches"].sections():
            search = SavedSearch(section)
            if section.has_option(self.POPULATE_LOOKUP_OPTION_KEY):
                populate_lookup_option = section.get_option(self.POPULATE_LOOKUP_OPTION_KEY)
                if populate_lookup_option.value.lower() in self.POPULATE_LOOKUP_ALLOW_VALUES:
                    yield WarningMessage(
                        f"The saved search {search.name} contains"
                        f" {self.POPULATE_LOOKUP_OPTION_KEY}, which is deprecated"
                        f" and will be removed in a future release.",
                        file_name=populate_lookup_option.get_relative_path(),
                        line_number=populate_lookup_option.get_line_number(),
                    )
                else:
                    yield FailMessage(
                        f"The saved search {search.name} contains"
                        f" {self.POPULATE_LOOKUP_OPTION_KEY} option which is not allowed in Splunk Cloud."
                        f" Remove this option from the savedsearch. ",
                        file_name=populate_lookup_option.get_relative_path(),
                        line_number=populate_lookup_option.get_line_number(),
                    )
