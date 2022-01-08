"""COVID Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
import pathlib
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from rich.console import Console

from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.alternative.covid import covid_view
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from gamestonk_terminal.menu import session

logger = logging.getLogger(__name__)
t_console = Console()

country_file = pathlib.Path(__file__).parent.joinpath("countries.txt")


class CovidController(BaseController):
    """Covid Controller class"""

    CHOICES_COMMANDS = ["country", "ov", "deaths", "cases", "rates", "slopes"]
    CHOICES_MENUS: List[str] = []

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/stocks/", queue, self.CHOICES_COMMANDS + self.CHOICES_MENUS)

        self.country = "US"
        self.COUNTRY_LIST = pd.read_csv(country_file, sep="\n", index_col=None)[
            "Countries"
        ].to_list()

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["country"] = {c: None for c in self.COUNTRY_LIST}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_str = f"""
        slopes      get countries with highest slope in cases
        country     select country for data

Country: [cyan]{self.country}[/cyan]

        ov          get overview (cases and deaths) for selected country
        deaths      get deaths for selected country
        cases       get cases for selected country
        rates       get death/cases rate for selected country
        """
        t_console.print(help_str)

    def custom_reset(self):
        """Class specific component of reset command"""
        self.queue.insert(self.reset_level, f"country {self.country}")

    def call_country(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="country",
            description="Select a country to look at data for.",
        )
        parser.add_argument(
            "-c",
            "--country",
            nargs="+",
            type=str,
            dest="country",
            help="Country to get data for.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.country:
                country = " ".join(ns_parser.country)
                if country not in self.COUNTRY_LIST:
                    t_console.print(f"[red]{country} not a valid selection.[/red]\n")
                    return
                self.country = country
                t_console.print(f"[cyan]{country}[/cyan] loaded\n")
            else:
                t_console.print("[red]Please input a country.[/red]\n")

    def call_ov(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ov",
            description="Show historical cases and deaths by country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_ov(
                self.country,
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_rates(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rates",
            description="Show historical rates country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="rates",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_deaths(self, other_args: List[str]):
        """Process deaths command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="deaths",
            description="Show historical deaths by country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="deaths",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_cases(self, other_args: List[str]):
        """Process cases command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cases",
            description="Show historical cases for country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="cases",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_slopes(self, other_args: List[str]):
        """Process cases command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="slopes",
            description="Show countries with highest slopes.",
        )
        parser.add_argument(
            "-d",
            "--days",
            type=check_positive,
            help="Number of days back to look",
            dest="days",
            default=30,
        )
        parser.add_argument(
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            help="Show in ascending order",
        )
        parser.add_argument(
            "-t",
            "--threshold",
            default=10000,
            dest="threshold",
            help="Threshold for total cases over period",
            type=check_positive,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )
        if ns_parser:
            covid_view.display_country_slopes(
                days_back=ns_parser.days,
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                threshold=ns_parser.threshold,
            )
