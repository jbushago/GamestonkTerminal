# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.comparison_analysis import yahoo_finance_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
def test_display_historical(mocker):
    # FORCE SINGLE THREADING
    yf_download = yahoo_finance_view.yahoo_finance_model.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    yahoo_finance_view.display_historical(
        similar_tickers=["TSLA", "GM"],
        start=datetime.strptime("2020-12-21", "%Y-%m-%d"),
        candle_type="o",
        normalize=True,
        export="",
    )


@pytest.mark.vcr
def test_display_volume(mocker):
    # FORCE SINGLE THREADING
    yf_download = yahoo_finance_view.yahoo_finance_model.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    yahoo_finance_view.display_volume(
        similar_tickers=["TSLA", "GM"],
        start=datetime.strptime("2020-12-21", "%Y-%m-%d"),
        export="",
    )


@pytest.mark.vcr
def test_display_correlation(mocker):
    # FORCE SINGLE THREADING
    yf_download = yahoo_finance_view.yahoo_finance_model.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    yahoo_finance_view.display_correlation(
        similar_tickers=["TSLA", "GM"],
        start=datetime.strptime("2020-12-21", "%Y-%m-%d"),
        candle_type="o",
    )
