"""Research Controller Module"""
__docformat__ = "numpy"

import webbrowser
from typing import List
from datetime import datetime
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.menu import session


class ResearchController(BaseController):
    """Research Controller class"""

    CHOICES_COMMANDS = [
        "macroaxis",
        "yahoo",
        "finviz",
        "marketwatch",
        "fool",
        "businessinsider",
        "fmp",
        "fidelity",
        "tradingview",
        "marketchameleon",
        "stockrow",
        "barchart",
        "grufity",
        "fintel",
        "zacks",
        "macrotrends",
        "newsfilter",
        "stockanalysis",
    ]
    CHOICES_MENUS: List[str] = []

    def __init__(
        self, ticker: str, start: datetime, interval: str, queue: List[str] = None
    ):
        """Constructor"""
        super().__init__(
            "/stocks/res/", queue, self.CHOICES_COMMANDS + self.CHOICES_MENUS
        )

        self.ticker = ticker
        self.start = start
        self.interval = interval

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
Ticker: {self.ticker}

    macroaxis            www.macroaxis.com
    yahoo                www.finance.yahoo.com
    finviz               www.finviz.com
    marketwatch          www.marketwatch.com
    fool                 www.fool.com
    businessinsider      www.markets.businessinsider.com
    fmp                  www.financialmodelingprep.com
    fidelity             www.eresearch.fidelity.com
    tradingview          www.tradingview.com
    marketchameleon      www.marketchameleon.com
    stockrow             www.stockrow.com
    barchart             www.barchart.com
    grufity              www.grufity.com
    fintel               www.fintel.com
    zacks                www.zacks.com
    macrotrends          www.macrotrends.net
    newsfilter           www.newsfilter.io
    stockanalysis        www.stockanalysis.com
"""
        print(help_text)

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            self.queue.insert(self.reset_level, f"load {self.ticker}")

    def call_macroaxis(self, _):
        """Process macroaxis command"""
        webbrowser.open(f"https://www.macroaxis.com/invest/market/{self.ticker}")
        print("")

    def call_yahoo(self, _):
        """Process yahoo command"""
        webbrowser.open(f"https://finance.yahoo.com/quote/{self.ticker}")
        print("")

    def call_finviz(self, _):
        """Process finviz command"""
        webbrowser.open(f"https://finviz.com/quote.ashx?t={self.ticker}")
        print("")

    def call_marketwatch(self, _):
        """Process marketwatch command"""
        webbrowser.open(f"https://www.marketwatch.com/investing/stock/{self.ticker}")
        print("")

    def call_fool(self, _):
        """Process fool command"""
        webbrowser.open(f"https://www.fool.com/quote/{self.ticker}")
        print("")

    def call_businessinsider(self, _):
        """Process businessinsider command"""
        webbrowser.open(
            f"https://markets.businessinsider.com/stocks/{self.ticker}-stock/"
        )
        print("")

    def call_fmp(self, _):
        """Process fmp command"""
        webbrowser.open(
            f"https://financialmodelingprep.com/financial-summary/{self.ticker}"
        )
        print("")

    def call_fidelity(self, _):
        """Process fidelity command"""
        webbrowser.open(
            f"https://eresearch.fidelity.com/eresearch/goto/evaluate/snapshot.jhtml?symbols={self.ticker}"
        )
        print("")

    def call_tradingview(self, _):
        """Process tradingview command"""
        webbrowser.open(f"https://www.tradingview.com/symbols/{self.ticker}")
        print("")

    def call_marketchameleon(self, _):
        """Process marketchameleon command"""
        webbrowser.open(f"https://marketchameleon.com/Overview/{self.ticker}")
        print("")

    def call_stockrow(self, _):
        """Process stockrow command"""
        webbrowser.open(f"https://stockrow.com/{self.ticker}")
        print("")

    def call_barchart(self, _):
        """Process barchart command"""
        webbrowser.open(
            f"https://www.barchart.com/stocks/quotes/{self.ticker}/overview"
        )
        print("")

    def call_grufity(self, _):
        """Process grufity command"""
        webbrowser.open(f"https://grufity.com/stock/{self.ticker}")
        print("")

    def call_fintel(self, _):
        """Process fintel command"""
        webbrowser.open(f"https://fintel.io/s/us/{self.ticker}")
        print("")

    def call_zacks(self, _):
        """Process zacks command"""
        webbrowser.open(f"https://www.zacks.com/stock/quote/{self.ticker}")
        print("")

    def call_macrotrends(self, _):
        """Process macrotrends command"""
        webbrowser.open(
            f"https://www.macrotrends.net/stocks/charts/{self.ticker}/{self.ticker}/market-cap"
        )
        print("")

    def call_newsfilter(self, _):
        """Process newsfilter command"""
        webbrowser.open(f"https://newsfilter.io/search?query={self.ticker}")
        print("")

    def call_stockanalysis(self, _):
        """Process stockanalysis command"""
        webbrowser.open(f"https://stockanalysis.com/stocks/{self.ticker}/")
        print("")
