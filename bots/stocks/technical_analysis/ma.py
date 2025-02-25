import logging

import plotly.graph_objects as go

from bots import imps, load_candle
from gamestonk_terminal.common.technical_analysis import overlap_model
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


# pylint: disable=R0913
@log_start_end(log=logger)
def ma_command(
    ticker="",
    interval: int = 15,
    past_days: int = 0,
    ma_mode="ema",
    window="",
    offset: int = 0,
    start="",
    end="",
    extended_hours: bool = False,
    heikin_candles: bool = False,
    news: bool = False,
):
    """Displays chart with selected Moving Average  [Yahoo Finance]"""
    # Debug
    if imps.DEBUG:
        # pylint: disable=logging-too-many-args
        logger.debug(
            "ta ma %s %s %s %s %s %s %s %s %s %s %s",
            ticker,
            interval,
            past_days,
            ma_mode,
            window,
            offset,
            start,
            end,
            extended_hours,
            heikin_candles,
            news,
        )

    # Check for argument
    overlap_ma = {
        "ema": overlap_model.ema,
        "hma": overlap_model.hma,
        "sma": overlap_model.sma,
        "wma": overlap_model.wma,
        "zlma": overlap_model.zlma,
    }

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

    if window == "":
        window = [20, 50]
    else:
        window_temp = list()
        for wind in window.split(","):
            try:
                window_temp.append(int(wind))
            except Exception as e:
                raise Exception("Window needs to be a float") from e
        window = window_temp

    df_ta = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

    if df_ta.empty:
        raise Exception("No Data Found")

    for win in window:
        ema_data = overlap_ma[ma_mode](
            values=df_ta["Adj Close"], length=win, offset=offset
        )
        df_ta = df_ta.join(ema_data)

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
    )
    title = f"<b>{plot['plt_title']} Moving Average ({ma_mode.upper()})</b>"
    fig = plot["fig"]

    for i in range(6, df_ta.shape[1]):
        fig.add_trace(
            go.Scatter(
                name=f"{df_ta.iloc[:, i].name}",
                mode="lines",
                x=df_ta.index,
                y=df_ta.iloc[:, i].values,
                opacity=1,
            ),
            secondary_y=True,
            row=1,
            col=1,
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=20),
        template=imps.PLT_TA_STYLE_TEMPLATE,
        colorway=imps.PLT_TA_COLORWAY,
        title=title,
        title_x=0.1,
        title_font_size=14,
        dragmode="pan",
    )
    imagefile = "ta_ma.png"

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
        "title": f"Stocks: Moving Average {ma_mode.upper()}",
        "description": plt_link,
        "imagefile": imagefile,
    }
