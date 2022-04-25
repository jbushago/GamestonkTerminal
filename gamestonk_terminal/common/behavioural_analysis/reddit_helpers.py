"""Reddit Helpers"""
__docformat__ = "numpy"

from typing import List
import re
import yfinance as yf

import praw


def find_all_body_tickers(ls_text: List[str]) -> List[str]:
    l_tickers_found = []
    for s_text in ls_text:
        print("s_text == " + s_text)
        for s_ticker in set(re.findall(r"(?<=\$)\w+|[A-Z]{3,6}", s_text)):
            print(s_ticker)
            l_tickers_found.append(s_ticker.strip())

    return l_tickers_found


def find_tickers(submission: praw.models.reddit.submission.Submission) -> List[str]:
    """Extracts potential tickers from reddit submission

    Parameters
    ----------
    submission : praw.models.reddit.submission.Submission
        Reddit post to scan

    Returns
    -------
    List[str]
        List of potential tickers
    """
    ls_text = [submission.selftext, submission.title]
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        ls_text.append(comment.body)

    return find_all_body_tickers(ls_text)


def get_subreddits_for_ticker(ticker: str) -> List[str]:
    """Returns appropriate list of subreddits for ticker

    Parameters
    ----------
    ticker : str
        ticker symbol

    Returns
    -------
    List[str]
        List of subreddits
    """
    subreddits = [
        "wallstreetbets",
        "stocks",
        "investing",
        "Daytrading",
        "pennystocks",
        "robinhood",
        "GME",
        "amcstock",
        "ethtrader",
        "investing",
        "Wallstreetbetsnew",
        "StockMarket",
        "options",
        "smallstreetbets",
        "weedstocks",
        "InvestmentClub",
        "ValueInvesting",
        "investing_discussion",
        "cryptocurrency",
        "dividends",
        "Economics",
        "EFTs",
    ]

    sector = get_ticker_sector(ticker)
    quote_type = get_ticker_quote_type(ticker)
    if sector:
        subreddits.extend(sector_to_subreddit_list(sector))
    if quote_type:
        subreddits.extend(quote_type_to_subreddit_list(quote_type))
    return subreddits


def ticker_to_name(ticker: str) -> str:
    """Returns the full name of ticker symbol

    Parameters
    ----------
    ticker : str
        ticker symbol of organization

    Returns
    -------
    str
        short name of ticker
    """
    suffixes = {
        "Corporation",
        "Incorporated",
        "Company",
        "Limited",
        "Corp.",
        "Inc.",
        "Co.",
        "Ltd.",
        "LLC",
    }
    name = yf.Ticker(ticker).info["shortName"].split(" ")
    cleaned_name = []
    for word in name:
        if word not in suffixes:
            cleaned_name.append(word)

    return " ".join(cleaned_name)


def get_ticker_sector(ticker: str) -> str:
    """Returns the sector of ticker symbol

    Parameters
    ----------
    ticker : str
        ticker symbol of organization

    Returns
    -------
    str
        sector of ticker
    """
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info
    return info["sector"] if "sector" in info else ""


def get_ticker_quote_type(ticker: str) -> str:
    """Returns the quote type of ticker symbol

    Parameters
    ----------
    ticker : str
        ticker symbol of organization

    Returns
    -------
    str
        quote type of ticker
    """
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info
    return info["quoteType"] if "quoteType" in info else ""


def sector_to_subreddit_list(sector: str) -> List[str]:
    """Returns list of subreddit for respective sector

    Parameters
    ----------
    sector : str
        sector of ticker

    Returns
    -------
    List[str]
        List of subreddits
    """
    sector_subreddit_map = {
        "Basic Materials": [],
        "Communication Services": [],
        "Consumer Cyclical": [],
        "Consumer Defensive": [],
        "Energy": [
            "energy",
            "RenewableEnergy",
        ],
        "Financial Services": [
            "Finance",
            "FinancialPlanning",
            "PersonalFinance",
        ],
        "Healthcare": [
            "public_health",
            "healthcare",
            "globalhealth",
        ],
        "Industrials": [],
        "Real Estate": [
            "realestate",
            "realestateinvesting",
        ],
        "Technology": [
            "technology",
            "tech",
        ],
        "Utilities": [],
    }

    return sector_subreddit_map[sector]


def quote_type_to_subreddit_list(quote_type: str) -> List[str]:
    """Returns list of subreddit for respective quote type

    Parameters
    ----------
    quote_type : str
        quote type of ticker

    Returns
    -------
    List[str]
        List of subreddits
    """
    quote_type_subreddit_map = {
        "EQUITY": [],
        "CRYPTOCURRENCY": [
            "cryptocurrencies",
            "cryptotechnology",
            "cryptomarkets",
            "binance",
        ],
        "ETF": [],
    }

    return quote_type_subreddit_map[quote_type]
