from unittest.mock import patch, Mock
import pandas as pd
from gamestonk_terminal import helper_funcs


@patch("gamestonk_terminal.helper_funcs.local_download")
def test_print_rich_table(local_download_mock):
    df = Mock(pd.DataFrame, create=True)
    helper_funcs.print_rich_table(df)

    assert local_download_mock.called_once_with(df, "csv")
