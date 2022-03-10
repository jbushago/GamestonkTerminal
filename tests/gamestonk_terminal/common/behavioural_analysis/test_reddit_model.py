from unittest import mock
import pytest
from gamestonk_terminal.common.behavioural_analysis import reddit_model
from unittest.mock import patch, Mock

    # @pytest.mark.parametrize(
    #     "get_posts_about",
    #     [
    #         #Tuple with input and expected
    #         ("0", tuple([[], dict, 0])),
    #     ],
    # )

@patch("praw.Reddit")
def test_get_posts_about(reddit_mock):
    api_mock = Mock()
    reddit_mock.return_value = api_mock
    api_mock.subreddit = Mock() 
    subreddit_mock = Mock()
    api_mock.subreddit.return_value = subreddit_mock
    mock_function = Mock()
    mock_function.return_value = [Mock(), Mock(), Mock(), Mock()]
    subreddit_mock.search = mock_function
    posts = reddit_model.get_posts_about(["MSFT", "Joey"], "MSFT", "day")
    api_mock.subreddit.assert_called_once_with("MSFT+Joey")
    mock_function.assert_called_once_with("MSFT", limit=100, time_filter="day")
