""" FINRA Model """
__docformat__ = "numpy"

import logging
from typing import Dict, List, Tuple

import pandas as pd
import requests
from scipy import stats

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def getFINRAweeks(tier: str, is_ats: bool) -> List:
    """Get FINRA weeks. [Source: FINRA]

    Parameters
    ----------
    tier : str
        Stock tier between T1, T2, or OTCE
    is_ats : bool
        ATS data if true, NON-ATS otherwise

    Returns
    -------
    List
        List of response data
    """
    req_hdr = {"Accept": "application/json", "Content-Type": "application/json"}

    req_data = {
        "compareFilters": [
            {
                "compareType": "EQUAL",
                "fieldName": "summaryTypeCode",
                "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
            },
            {
                "compareType": "EQUAL",
                "fieldName": "tierIdentifier",
                "fieldValue": tier,
            },
        ],
        "delimiter": "|",
        "fields": ["weekStartDate"],
        "limit": 27,
        "quoteValues": False,
        "sortFields": ["-weekStartDate"],
    }

    response = requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklyDownloadDetails",
        headers=req_hdr,
        json=req_data,
    )

    return response.json() if response.status_code == 200 else list()


def getFINRAdata_offset(
    weekStartDate: str, tier: str, ticker: str, is_ats: bool, offset: int
) -> requests.Response:
    """Get FINRA data. [Source: FINRA]

    Parameters
    ----------
    weekStartDate : str
        Weekly data to get FINRA data
    tier : str
        Stock tier between T1, T2, or OTCE
    ticker : str
        Stock ticker to get data from
    is_ats : bool
        ATS data if true, NON-ATS otherwise
    offset : int
        Offset in getting the data

    Returns
    -------
    requests.Response
        Response from FINRA data
    """
    req_hdr = {"Accept": "application/json", "Content-Type": "application/json"}

    l_cmp_filters = [
        {
            "compareType": "EQUAL",
            "fieldName": "weekStartDate",
            "fieldValue": weekStartDate,
        },
        {"compareType": "EQUAL", "fieldName": "tierIdentifier", "fieldValue": tier},
        {
            "compareType": "EQUAL",
            "description": "",
            "fieldName": "summaryTypeCode",
            "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
        },
    ]

    if ticker:
        l_cmp_filters.append(
            {
                "compareType": "EQUAL",
                "fieldName": "issueSymbolIdentifier",
                "fieldValue": ticker,
            }
        )

    req_data = {
        "compareFilters": l_cmp_filters,
        "delimiter": "|",
        "fields": [
            "issueSymbolIdentifier",
            "totalWeeklyShareQuantity",
            "totalWeeklyTradeCount",
            "lastUpdateDate",
        ],
        "limit": 5000,
        "offset": offset,
        "quoteValues": False,
        "sortFields": ["totalWeeklyShareQuantity"],
    }

    return requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklySummary",
        headers=req_hdr,
        json=req_data,
    )


def getFINRAdata(
    weekStartDate: str, tier: str, ticker: str, is_ats: bool
) -> Tuple[int, List]:
    """Get FINRA data. [Source: FINRA]

    Parameters
    ----------
    weekStartDate : str
        Weekly data to get FINRA data
    tier : str
        Stock tier between T1, T2, or OTCE
    ticker : str
        Stock ticker to get data from
    is_ats : bool
        ATS data if true, NON-ATS otherwise

    Returns
    -------
    int
        Status code from request
    List
        List of response data
    """
    req_hdr = {"Accept": "application/json", "Content-Type": "application/json"}

    l_cmp_filters = [
        {
            "compareType": "EQUAL",
            "fieldName": "weekStartDate",
            "fieldValue": weekStartDate,
        },
        {"compareType": "EQUAL", "fieldName": "tierIdentifier", "fieldValue": tier},
        {
            "compareType": "EQUAL",
            "description": "",
            "fieldName": "summaryTypeCode",
            "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
        },
    ]

    if ticker:
        l_cmp_filters.append(
            {
                "compareType": "EQUAL",
                "fieldName": "issueSymbolIdentifier",
                "fieldValue": ticker,
            }
        )

    req_data = {
        "compareFilters": l_cmp_filters,
        "delimiter": "|",
        "fields": [
            "issueSymbolIdentifier",
            "totalWeeklyShareQuantity",
            "totalWeeklyTradeCount",
            "lastUpdateDate",
        ],
        "limit": 5000,
        "quoteValues": False,
        "sortFields": ["totalWeeklyShareQuantity"],
    }

    response = requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklySummary",
        headers=req_hdr,
        json=req_data,
    )

    return (
        response.status_code,
        response.json() if response.status_code == 200 else list(),
    )


@log_start_end(log=logger)
def getATSdata(num_tickers_to_filter: int, tier_ats: str) -> Tuple[pd.DataFrame, Dict]:
    """Get all FINRA ATS data, and parse most promising tickers based on linear regression

    Parameters
    ----------
    num_tickers_to_filter : int
        Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity
    tier_ats : int
        Tier to process data from

    Returns
    -------
    pd.DataFrame
        Dark Pools (ATS) Data
    Dict
        Tickers from Dark Pools with better regression slope
    """
    if tier_ats:
        tiers = [tier_ats]
    else:
        tiers = ["T1", "T2", "OTCE"]
    df_ats = pd.DataFrame()

    for tier in tiers:
        console.print(f"Processing Tier {tier} ...")
        for d_week in getFINRAweeks(tier, is_ats=True):
            offset = 0
            response = getFINRAdata_offset(
                d_week["weekStartDate"], tier, "", True, offset
            )
            l_data = response.json()

            while len(response.json()) == 5000:
                offset += 5000
                response = getFINRAdata_offset(
                    d_week["weekStartDate"], tier, "", True, offset
                )
                l_data += response.json()

            df_ats_week = pd.DataFrame(l_data)
            df_ats_week["weekStartDate"] = d_week["weekStartDate"]

            if not df_ats_week.empty:
                df_ats = df_ats.append(df_ats_week, ignore_index=True)

    df_ats = df_ats.sort_values("weekStartDate")
    df_ats["weekStartDateInt"] = pd.to_datetime(df_ats["weekStartDate"]).apply(
        lambda x: x.timestamp()
    )

    console.print(
        f"Processing regression on {num_tickers_to_filter} promising tickers ..."
    )

    d_ats_reg = {}
    # set(df_ats['issueSymbolIdentifier'].values) this would be iterating through all tickers
    # but that is extremely time consuming for little reward. A little filtering is done to
    # speed up search for best ATS tickers
    for symbol in list(
        df_ats.groupby("issueSymbolIdentifier")["totalWeeklyShareQuantity"]
        .sum()
        .sort_values()[-num_tickers_to_filter:]
        .index
    ):
        try:
            slope = stats.linregress(
                df_ats[df_ats["issueSymbolIdentifier"] == symbol][
                    "weekStartDateInt"
                ].values,
                df_ats[df_ats["issueSymbolIdentifier"] == symbol][
                    "totalWeeklyShareQuantity"
                ].values,
            )[0]
            d_ats_reg[symbol] = slope
        except Exception:
            pass

    return df_ats, d_ats_reg


@log_start_end(log=logger)
def getTickerFINRAdata(ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get all FINRA data associated with a ticker

    Parameters
    ----------
    ticker : str
        Stock ticker to get data from

    Returns
    -------
    pd.DataFrame
        Dark Pools (ATS) Data
    pd.DataFrame
        OTC (Non-ATS) Data
    """
    tiers = ["T1", "T2", "OTCE"]

    l_data = []
    for tier in tiers:
        for d_week in getFINRAweeks(tier, is_ats=True):
            status_code, response = getFINRAdata(
                d_week["weekStartDate"], tier, ticker, True
            )
            if status_code == 200:
                if response:
                    d_data = response[0]
                    d_data.update(d_week)
                    l_data.append(d_data)
                else:
                    break

    df_ats = pd.DataFrame(l_data)
    if not df_ats.empty:
        df_ats = df_ats.sort_values("weekStartDate")
        df_ats = df_ats.set_index("weekStartDate")

    l_data = []
    for tier in tiers:
        for d_week in getFINRAweeks(tier, is_ats=False):
            status_code, response = getFINRAdata(
                d_week["weekStartDate"], tier, ticker, False
            )
            if status_code == 200:
                if response:
                    d_data = response[0]
                    d_data.update(d_week)
                    l_data.append(d_data)
                else:
                    break

    df_otc = pd.DataFrame(l_data)
    if not df_otc.empty:
        df_otc = df_otc.sort_values("weekStartDate")
        df_otc = df_otc.set_index("weekStartDate")

    return df_ats, df_otc
