""" Due Diligence Controller """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime, timedelta
from pandas.core.frame import DataFrame
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.decorators import try_except
from gamestonk_terminal.stocks.due_diligence import (
    fmp_view,
    business_insider_view,
    finviz_view,
    marketwatch_view,
    finnhub_view,
    csimarket_view,
    ark_view,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks import stocks_helper


class DueDiligenceController(BaseController):
    """Due Diligence Controller"""

    CHOICES_COMMANDS = [
        "load",
        "sec",
        "rating",
        "pt",
        "rot",
        "est",
        "analyst",
        "supplier",
        "customer",
        "arktrades",
    ]

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        super().__init__("/stocks/dd/", queue)

        self.choices += self.CHOICES_COMMANDS

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["load"]["-i"] = {c: {} for c in stocks_helper.INTERVALS}
            choices["load"]["-s"] = {c: {} for c in stocks_helper.SOURCES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
Ticker: {self.ticker}

Finviz:
    analyst       analyst prices and ratings of the company
FMP:
    rating        rating over time (daily)
Finnhub:
    rot           number of analysts ratings over time (monthly)
Business Insider:
    pt            price targets over time
    est           quarter and year analysts earnings estimates
Market Watch:
    sec           SEC filings
csimarket:
    supplier      list of suppliers
    customer      list of customers
cathiesark.com
    arktrades     get ARK trades for ticker
        """
        print(help_text)

    def custom_reset(self, _):
        """Class specific component of reset command"""
        if self.ticker:
            self.queue.insert(4, f"load {self.ticker}")

    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be"
            " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=int,
            default=1440,
            choices=stocks_helper.INTERVALS,
            help="Intraday stock minutes",
        )
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=stocks_helper.SOURCES,
            default="yf",
            help="Source of historical data.",
        )
        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            df_stock_candidate = stocks_helper.load(
                ticker=ns_parser.ticker,
                start=ns_parser.start,
                interval=ns_parser.interval,
                source=ns_parser.source,
            )

            if not df_stock_candidate.empty:
                self.stock = df_stock_candidate
                self.start = ns_parser.start
                if "." in ns_parser.ticker:
                    self.ticker = ns_parser.ticker.upper().split(".")[0]
                else:
                    self.ticker = ns_parser.ticker.upper()

    @try_except
    def call_analyst(self, other_args: List[str]):
        """Process analyst command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="analyst",
            description="""
                Print analyst prices and ratings of the company. The following fields are expected:
                date, analyst, category, price from, price to, and rating. [Source: Finviz]
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.analyst(ticker=self.ticker, export=ns_parser.export)

    @try_except
    def call_pt(self, other_args: List[str]):
        """Process pt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pt",
            description="""Prints price target from analysts. [Source: Business Insider]""",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of latest price targets from analysts to print.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            business_insider_view.price_target_from_analysts(
                ticker=self.ticker,
                start=self.start,
                interval=self.interval,
                stock=self.stock,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @try_except
    def call_est(self, other_args: List[str]):
        """Process est command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="est",
            description="""Yearly estimates and quarter earnings/revenues. [Source: Business Insider]""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            business_insider_view.estimates(
                ticker=self.ticker,
                export=ns_parser.export,
            )

    @try_except
    def call_rot(self, other_args: List[str]):
        """Process rot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rot",
            description="""
                Rating over time (monthly). [Source: Finnhub]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of last months",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finnhub_view.rating_over_time(
                ticker=self.ticker,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @try_except
    def call_rating(self, other_args: List[str]):
        """Process rating command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rating",
            description="""
                Based on specific ratios, prints information whether the company
                is a (strong) buy, neutral or a (strong) sell. The following fields are expected:
                P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of last days to display ratings",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.rating(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_sec(self, other_args: List[str]):
        """Process sec command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="sec",
            description="""
                Prints SEC filings of the company. The following fields are expected: Filing Date,
                Document Date, Type, Category, Amended, and Link. [Source: Market Watch]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="number of latest SEC filings.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.sec_filings(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_supplier(self, other_args: List[str]):
        """Process supplier command"""
        parser = argparse.ArgumentParser(
            prog="supplier",
            add_help=False,
            description="List of suppliers from ticker provided. [Source: CSIMarket]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            csimarket_view.suppliers(
                ticker=self.ticker,
                export=ns_parser.export,
            )

    def call_customer(self, other_args: List[str]):
        """Process customer command"""
        parser = argparse.ArgumentParser(
            prog="customer",
            add_help=False,
            description="List of customers from ticker provided. [Source: CSIMarket]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            csimarket_view.customers(
                ticker=self.ticker,
                export=ns_parser.export,
            )

    @try_except
    def call_arktrades(self, other_args):
        """Process arktrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="arktrades",
            description="""
                Get trades for ticker across all ARK funds.
            """,
        )
        parser.add_argument(
            "-l",
            "--limi",
            help="Limit of rows to show",
            dest="limit",
            default=10,
            type=check_positive,
        )
        parser.add_argument(
            "-s",
            "--show_ticker",
            action="store_true",
            default=False,
            help="Flag to show ticker in table",
            dest="show_ticker",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ark_view.display_ark_trades(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
                show_ticker=ns_parser.show_ticker,
            )
