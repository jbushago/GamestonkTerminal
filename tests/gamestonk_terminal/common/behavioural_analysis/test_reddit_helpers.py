#IMPORTANT INTERNAL
from gamestonk_terminal.common.behavioural_analysis import reddit_helpers

def test_find_tickers(expected, mocker):
    mocker.patch(
        target="gamestonk_terminal.common.behavioural_analysis.reddit_helpers"
    )