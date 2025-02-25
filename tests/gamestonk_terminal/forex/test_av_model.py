# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.forex import av_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "from_symbol, to_symbol",
    [
        ("EUR", "USD"),
        ("USD", "JPY"),
        ("GBP", "EUR"),
        ("CHF", "USD"),
    ],
)
def test_get_historical(from_symbol, to_symbol, recorder):
    result = av_model.get_historical(
        to_symbol=to_symbol,
        from_symbol=from_symbol,
    )
    recorder.capture(result)
