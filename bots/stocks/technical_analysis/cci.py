import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.decorators import log_start_end

# pylint: disable=R0913
logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def cci_command(
    ticker: str = "",
    interval: int = 15,
    past_days: int = 0,
    length="14",
    scalar="0.015",
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with commodity channel index [Yahoo Finance]"""

    # Debug
    if imps.DEBUG:
        logger.debug(
            "ta cci %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            length,
            scalar,
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

    # pylint
    try:
        length = int(length)
    except ValueError as e:
        raise Exception("Length has to be an integer") from e
    try:
        scalar = float(scalar)
    except ValueError as e:
        raise Exception("Scalar has to be an integer") from e

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    if df_ta.empty:
        raise Exception("No Data Found")

    ta_data = momentum_model.cci(
        df_ta["High"], df_ta["Low"], df_ta["Adj Close"], length, scalar
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
    title = f"<b>{plot['plt_title']} Commodity-Channel-Index</b>"
    fig = plot["fig"]

    dmin = df_ta.iloc[:, 6].values.values.min()
    dmax = df_ta.iloc[:, 6].values.values.max()
    fig.add_trace(
        go.Scatter(
            name=f"CCI  ({length})  ({scalar})",
            mode="lines",
            x=df_ta.index,
            y=df_ta.iloc[:, 6].values,
            opacity=1,
        ),
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=100,
        y1=dmax,
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0,
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=-100,
        y1=dmin,
        fillcolor="green",
        opacity=0.2,
        layer="below",
        line_width=0,
        row=2,
        col=1,
    )
    fig.add_hline(
        y=-100,
        fillcolor="green",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="green", dash="dash"),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=100,
        fillcolor="red",
        opacity=1,
        layer="below",
        line_width=3,
        line=dict(color="red", dash="dash"),
        row=2,
        col=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=title,
        title_x=0.02,
        title_font_size=14,
        dragmode="pan",
    )
    imagefile = "ta_cci.png"

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
        "title": f"Stocks: Commodity-Channel-Index {ticker.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
