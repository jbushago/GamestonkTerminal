from unittest import TestCase

import vcr
import pytest
from gamestonk_terminal.cryptocurrency.discovery import (
    pycoingecko_view as disc_pycoingecko_view,
)

from tests.helpers.helpers import check_print

# pylint: disable=unused-import


# pylint: disable=R0904
class TestCoinGeckoAPI(TestCase):
    @pytest.mark.skip
    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/gainers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_gainers(self):
        disc_pycoingecko_view.display_gainers(period="24h", top=15, export="")

    @pytest.mark.skip
    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/losers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_losers(self):
        disc_pycoingecko_view.display_losers(period="24h", top=15, export="")

    @pytest.mark.skip
    @check_print(assert_in="CryptoBlades")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/discover.yaml",
        record_mode="new_episodes",
    )
    def test_coin_discover(self):
        disc_pycoingecko_view.display_trending(
            export="",
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/top_volume_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_volume_coins(self):
        disc_pycoingecko_view.display_top_volume_coins(
            top=15,
            export="",  # sortby="Rank", descend=True,
        )

    @pytest.mark.skip
    @check_print(assert_in="═════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/top_defi_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_defi_coins(self):
        disc_pycoingecko_view.display_top_defi_coins(
            top=15, export=""  # sortby="Rank", descend=True, links=False,
        )
