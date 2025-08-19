# import argparse and create a function to parse command line arguments
# and return the parsed arguments, which will be used by the main function
# to get the start and end dates for the pull requests and the organization
# name
from __future__ import annotations

import argparse
import importlib.metadata
import sys
from datetime import datetime, timedelta, timezone

from reviewtally.exceptions.local_exceptions import MalformedDateError


def print_toml_version() -> None:
    version = importlib.metadata.version("review-tally")
    print(f"Current version is {version}")  # noqa: T201


def parse_cmd_line() -> tuple[
    str,
    datetime,
    datetime,
    list[str],
    list[str],
    bool,
    str | None,
]:  # type: ignore[return-value]
    description = """Get pull requests for the organization between dates
    and the reviewers for each pull request. The environment must declare
    a GTIHUB_TOKEN variable with a valid GitHub token.
    """
    org_help = "Organization name"
    start_date_help = "Start date in the format YYYY-MM-DD"
    end_date_help = "End date in the format YYYY-MM-DD"
    language_selection = "Select the language to filter the pull requests"
    parser = argparse.ArgumentParser(description=description)
    # these arguments are required
    parser.add_argument("-o", "--org", required=False, help=org_help)
    date_format = "%Y-%m-%d"
    two_weeks_ago = datetime.now(tz=timezone.utc) - timedelta(days=14)
    today = datetime.now(tz=timezone.utc)
    parser.add_argument(
        "-s",
        "--start_date",
        required=False,
        help=start_date_help,
        default=two_weeks_ago.strftime(date_format),
    )
    parser.add_argument(
        "-e",
        "--end_date",
        required=False,
        help=end_date_help,
        default=today.strftime(date_format),
    )
    # add the language selection argument
    parser.add_argument(
        "-l",
        "--language",
        required=False,
        help=language_selection,
    )
    # add the metrics selection argument
    metrics_help = (
        "Comma-separated list of metrics to display "
        "(reviews,comments,avg-comments,engagement,thoroughness,response-time,completion-time,active-days)"
    )
    parser.add_argument(
        "-m",
        "--metrics",
        required=False,
        default="reviews,comments,avg-comments",
        help=metrics_help,
    )
    version_help = """
    Print version and exit
    """
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help=version_help,
    )
    # add sprint analysis arguments
    parser.add_argument(
        "--sprint-analysis",
        action="store_true",
        help="Generate sprint-based team aggregation as CSV",
    )
    parser.add_argument(
        "--output-path",
        help="Output CSV file path for sprint data",
    )
    args = parser.parse_args()
    # catch ValueError if the date format is not correct
    try:
        if args.start_date:
            start_date = (
                datetime.strptime(args.start_date, "%Y-%m-%d")
            ).replace(tzinfo=timezone.utc)
    except ValueError:
        print(MalformedDateError(args.start_date))  # noqa: T201
        sys.exit(1)
    try:
        if args.end_date:
            end_date = (datetime.strptime(args.end_date, "%Y-%m-%d")).replace(
                tzinfo=timezone.utc,
            )
    except ValueError:
        print(MalformedDateError(args.end_date))  # noqa: T201
        sys.exit(1)
    if args.version:
        print_toml_version()
        sys.exit(0)
    if start_date > end_date:
        print("Error: Start date must be before end date")  # noqa: T201
        sys.exit(1)
    # if the language arg has comma separated values, split them
    if args.language is None:
        languages = []
    elif args.language and "," in args.language:
        languages = args.language.split(",")
    else:
        languages = [args.language]

    # parse metrics argument
    if args.metrics and "," in args.metrics:
        metrics = args.metrics.split(",")
    else:
        metrics = [args.metrics]

    return (
        args.org,
        start_date,
        end_date,
        languages,
        metrics,
        args.sprint_analysis,
        args.output_path,
    )
