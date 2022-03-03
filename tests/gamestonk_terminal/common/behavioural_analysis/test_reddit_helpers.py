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
