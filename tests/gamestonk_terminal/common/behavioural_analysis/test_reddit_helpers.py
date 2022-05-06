# IMPORTANT INTERNAL
import pytest
from gamestonk_terminal.common.behavioural_analysis import reddit_helpers


@pytest.mark.parametrize(
    "mocked_input , expected",
    [
        (
            [
                "$MSFT, $BABA, ECE49595 is the best, lets go! Diamond hands all the way. DOGE to the moon."
            ],
            ["MSFT", "BABA", "ECE", "DOGE"],
        ),
        ("", []),
        ("Arsenal is the best football club in the world", []),
    ],
)
def test_find_tickers(mocked_input, expected):
    generated_tickers = reddit_helpers.find_all_body_tickers(mocked_input)
    assert set(generated_tickers) == set(expected)

@pytest.mark.vcr
def test_get_subreddits_for_ticker():
    ticker = "MSFT"
    subreddits = reddit_helpers.get_subreddits_for_ticker(ticker)
    assert subreddits


@pytest.mark.vcr
def test_ticker_to_name():
    ticker = "MSFT"
    sector = reddit_helpers.ticker_to_name(ticker)
    assert sector == "Microsoft"


@pytest.mark.vcr
def test_get_ticker_sector():
    ticker = "TWTR"
    sector = reddit_helpers.get_ticker_sector(ticker)
    assert sector == "Communication Services"


@pytest.mark.vcr
def test_get_ticker_quote_type():
    ticker = "TWTR"
    sector = reddit_helpers.get_ticker_quote_type(ticker)
    assert sector == "EQUITY"


@pytest.mark.parametrize("input", ["Technology", "Healthcare"])
@pytest.mark.parametrize(
    "expected",
    [
        [
            "technology",
            "tech",
        ],
        [
            "public_health",
            "healthcare",
            "globalhealth",
        ],
    ],
)
def sector_to_subreddit_list(input, expected):
    assert reddit_helpers.sector_to_subreddit_list(input) == expected


@pytest.mark.parametrize("input", ["EQUITY", "CRYPTOCURRENCY"])
@pytest.mark.parametrize(
    "expected",
    [
        [],
        [
            "cryptocurrencies",
            "cryptotechnology",
            "cryptomarkets",
            "binance",
        ],
    ],
)
def quote_type_to_subreddit_list(input, expected):
    assert reddit_helpers.quote_type_to_subreddit_list(input) == expected
