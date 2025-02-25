import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from gamestonk_terminal.common.technical_analysis import trend_indicators_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


# pylint: disable=R0913
@log_start_end(log=logger)
def adx_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    length="14",
    scalar="100",
    drift="1",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with average directional movement index [Yahoo Finance]"""

    # Debug
    if imps.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta adx %s %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            drift,
            start,
            end,
            extended_hours,
            heikin_candles,
            news,
        )

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    # Retrieve Data
    df_stock, start, end, bar_start = load_candle.stock_data(
        ticker=ticker,
        interval=interval,
        past_days=past_days,
        extended_hours=extended_hours,
        start=start,
        end=end,
        heikin_candles=heikin_candles,
    )

    if df_stock.empty:
        raise Exception("No Data Found")

    if not length.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    length = float(length)
    if not scalar.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    scalar = float(scalar)
    if not drift.lstrip("-").isnumeric():
        raise Exception("Number has to be an integer")
    drift = float(drift)

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    if df_ta.empty:
        raise Exception("No Data Found")

    ta_data = trend_indicators_model.adx(
        df_stock["High"],
        df_stock["Low"],
        df_stock["Adj Close"],
        length,
        scalar,
        drift,
    )
    df_ta = df_ta.join(ta_data)

    # Output Data
    if interval != 1440:
        df_ta = df_ta.loc[(df_ta.index >= bar_start) & (df_ta.index < end)]

    plot = load_candle.candle_fig(
        df_ta,
        ticker,
        interval,
        extended_hours,
        news,
        bar=bar_start,
        int_bar=interval,
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        row_width=[0.4, 0.6],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    )
    title = f"<b>{plot['plt_title']} Average Directional Movement Index</b>"
    fig = plot["fig"]

    fig.add_trace(
        go.Scatter(
            name=f"ADX ({length})",
            mode="lines",
            x=df_ta.index,
            y=df_ta.iloc[:, 6].values,
            opacity=1,
            line=dict(width=2),
        ),
        secondary_y=False,
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            name=f"+DI ({length})",
            mode="lines",
            x=df_ta.index,
            y=df_ta.iloc[:, 7].values,
            opacity=1,
            line=dict(width=1),
        ),
        secondary_y=False,
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            name=f"-DI ({length})",
            mode="lines",
            x=df_ta.index,
            y=df_ta.iloc[:, 8].values,
            opacity=1,
            line=dict(width=1),
        ),
        secondary_y=False,
        row=2,
        col=1,
    )
    fig.add_hline(
        y=25,
        fillcolor="grey",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="grey", dash="dash"),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=title,
        title_x=0.01,
        title_font_size=12,
        dragmode="pan",
    )
    imagefile = "ta_adx.png"

    # Check if interactive settings are enabled
    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)

    fig.update_layout(
        width=800,
        height=500,
    )

    imagefile = imps.image_border(imagefile, fig=fig)

    return {
        "title": f"Stocks: Average-Directional-Movement-Index {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
