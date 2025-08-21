import os
from typing_extensions import Callable, Literal, Optional, TypedDict
import ta
import ta.volume
import ta.trend
import ta.momentum
import ta.volatility

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

available_indicators = [
    "BB",
    "Trend",
    "EMA",
    "MACD",
    "RSI",
    "SMA",
    "TEMA",
    "ATR",
    "STOCH",
    "ADX",
    "OBV",
    "MFI",
    "CCI",
]


def indicators_from_close(close: pd.Series, indicators: list[str] = []) -> dict[str, pd.Series]:
    indicator: dict[str, pd.Series] = {}
    if "BB" in indicators:
        band = ta.volatility.BollingerBands(close)
        indicator["lowerband"] = band.bollinger_lband()
        indicator["middleband"] = band.bollinger_mavg()
        indicator["upperband"] = band.bollinger_hband()
    if "Trend" in indicators:
        indicator["trend"] = close.ewm(span=20, adjust=False).mean()
    if "MACD" in indicators:
        macd = ta.trend.MACD(close)
        indicator["macd"] = macd.macd()
        indicator["macd_signal"] = macd.macd_signal()
        indicator["macd_hist"] = macd.macd_diff()
    if "RSI" in indicators:
        indicator["rsi"] = ta.momentum.rsi(close)
    if "EMA" in indicators:
        indicator["ema5"] = ta.trend.ema_indicator(close, window=5)
        indicator["ema10"] = ta.trend.ema_indicator(close, window=10)
        indicator["ema50"] = ta.trend.ema_indicator(close, window=50)
        indicator["ema100"] = ta.trend.ema_indicator(close, window=100)
    if "SMA" in indicators:
        indicator["sma"] = ta.trend.sma_indicator(close, window=40)
    if "TEMA" in indicators:
        indicator["tema"] = ta.trend.ema_indicator(close, window=9)
    return indicator


def indicators_from_close_volume_high_low(close: pd.Series, volume: pd.Series, high: pd.Series, low: pd.Series, indicators: list[str] = []):
    indicator: dict[str, pd.Series] = {}
    if "ATR" in indicators:
        indicator["atr"] = ta.volatility.average_true_range(high=close, low=close, close=close, window=14)
    if "OBV" in indicators:
        indicator["obv"] = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
    if "ADX" in indicators:
        indicator["adx"] = ta.trend.adx(high, low, close)
    if "STOCH" in indicators:
        indicator["fastd"] = ta.momentum.stoch_signal(high, low, close)
        indicator["fastk"] = ta.momentum.stoch(high, low, close)
    if "MFI" in indicators:
        indicator["mfi"] = ta.volume.MFIIndicator(high, low, close, volume).money_flow_index()
    if "CCI" in indicators:
        indicator["cci"] = ta.trend.cci(high, low, close, window=20)
    return indicator


def add_indicators_to_figure(
    fig: go.Figure,
    row_id: int,
    indicator: str,
    ind: dict[str, pd.Series],
    last_timestamp: pd.Timestamp,
) -> go.Figure:
    """
    将技术指标添加到图表中

    Args:
        fig (go.Figure): Plotly 图表对象
        row_id (int): 指标所在的行号
        indicator (str): 指标名称
        ind (dict[str, pd.Series]): 技术指标数据
        last_timestamp (pd.Timestamp): 最后一个时间戳，用于添加分割线

    Returns:
        go.Figure: 更新后的图表对象
    """
    if indicator == "BB":
        fig.add_trace(go.Scatter(x=ind["upperband"].index, y=ind["upperband"], mode="lines", name="upper band", line=dict(color="green", width=2)), row=row_id, col=1)
        fig.add_trace(go.Scatter(x=ind["middleband"].index, y=ind["middleband"], mode="lines", name="middle band", line=dict(color="orange", width=2)), row=row_id, col=1)
        fig.add_trace(go.Scatter(x=ind["lowerband"].index, y=ind["lowerband"], mode="lines", name="lower band", line=dict(color="red", width=2)), row=row_id, col=1)
        last_upper = ind["upperband"][last_timestamp]
        last_middle = ind["middleband"][last_timestamp]
        last_lower = ind["lowerband"][last_timestamp]
        print(f"BB: {last_upper}, {last_middle}, {last_lower}")
        # 在图表上添加BB指标的最后值
        fig.add_annotation(
            x=ind["upperband"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:green'>Upper Band: {last_upper:.4f}</span>  <span style='color:orange'>Middle Band: {last_middle:.4f}</span>  <span style='color:red'>Lower Band: {last_lower:.4f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min = min(ind["lowerband"].min(), ind["middleband"].min(), ind["upperband"].min())
        y_max = max(ind["lowerband"].max(), ind["middleband"].max(), ind["upperband"].max())
    elif indicator == "Trend":
        # 添加趋势线
        fig.add_trace(go.Scatter(x=ind["trend"].index, y=ind["trend"], name="Trend", line=dict(color="blue", width=1)), row=row_id, col=1)
        last_trend = ind["trend"][last_timestamp]
        # 在图表上添加趋势线的最后值
        fig.add_annotation(
            x=ind["trend"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:blue'>Trend: {last_trend:.4f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min = ind["trend"].min()
        y_max = ind["trend"].max()
    elif indicator == "EMA":
        # 添加EMA指标
        fig.add_trace(go.Scatter(x=ind["ema5"].index, y=ind["ema5"], name="EMA 5", line=dict(color="blue", width=1)), row=row_id, col=1)
        fig.add_trace(go.Scatter(x=ind["ema10"].index, y=ind["ema10"], name="EMA 10", line=dict(color="orange", width=1)), row=row_id, col=1)
        fig.add_trace(go.Scatter(x=ind["ema50"].index, y=ind["ema50"], name="EMA 50", line=dict(color="green", width=1)), row=row_id, col=1)
        fig.add_trace(go.Scatter(x=ind["ema100"].index, y=ind["ema100"], name="EMA 100", line=dict(color="red", width=1)), row=row_id, col=1)
        last_ema5 = ind["ema5"][last_timestamp]
        last_ema10 = ind["ema10"][last_timestamp]
        last_ema50 = ind["ema50"][last_timestamp]
        last_ema100 = ind["ema100"][last_timestamp]
        # 在图表上添加EMA指标的最后值
        fig.add_annotation(
            x=ind["ema5"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:blue'>EMA 5: {last_ema5:.4f}</span>  <span style='color:orange'>EMA 10: {last_ema10:.4f}</span>  <span style='color:green'>EMA 50: {last_ema50:.4f}</span>  <span style='color:red'>EMA 100: {last_ema100:.4f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min = min(ind["ema5"].min(), ind["ema10"].min(), ind["ema50"].min(), ind["ema100"].min())
        y_max = max(ind["ema5"].max(), ind["ema10"].max(), ind["ema50"].max(), ind["ema100"].max())
    elif indicator == "MACD":
        # 添加MACD指标
        fig.add_trace(go.Scatter(x=ind["macd"].index, y=ind["macd"], name="MACD", line=dict(color="blue", width=1)), row=row_id, col=1)
        fig.add_trace(go.Scatter(x=ind["macd_signal"].index, y=ind["macd_signal"], name="MACD Signal", line=dict(color="orange", width=1)), row=row_id, col=1)
        colors = ["green" if val >= 0 else "red" for val in ind["macd_hist"]]
        fig.add_trace(go.Bar(x=ind["macd_hist"].index, y=ind["macd_hist"], name="MACD Histogram", marker_color=colors), row=row_id, col=1)
        last_macd = ind["macd"][last_timestamp]
        last_signal = ind["macd_signal"][last_timestamp]
        last_hist = ind["macd_hist"][last_timestamp]
        # 在图表上添加MACD指标的最后值
        fig.add_annotation(
            x=ind["macd"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:blue'>MACD: {last_macd:.4f}</span>  <span style='color:orange'>Signal: {last_signal:.4f}</span>  <span style='color:{'green' if last_hist >= 0 else 'red'}'>Histogram: {last_hist:.4f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )

        y_min = min(ind["macd"].min(), ind["macd_signal"].min(), ind["macd_hist"].min())
        y_max = max(ind["macd"].max(), ind["macd_signal"].max(), ind["macd_hist"].max())
    elif indicator == "RSI":
        # 添加RSI指标
        fig.add_trace(go.Scatter(x=ind["rsi"].index, y=ind["rsi"], name="RSI", line=dict(color="purple", width=1)), row=row_id, col=1)
        # 添加RSI超买超卖线
        fig.add_shape(type="line", x0=ind["rsi"].index[0], y0=70, x1=ind["rsi"].index[-1], y1=70, name="Overbought", line=dict(color="red", width=1, dash="dash"), row=row_id, col=1)
        fig.add_shape(type="line", x0=ind["rsi"].index[0], y0=30, x1=ind["rsi"].index[-1], y1=30, name="Oversold", line=dict(color="green", width=1, dash="dash"), row=row_id, col=1)
        last_rsi = ind["rsi"][last_timestamp]
        fig.add_annotation(
            x=ind["rsi"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:purple'>RSI: {last_rsi:.2f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min, y_max = 0, 100
    elif indicator == "ADX":
        # 添加ADX指标
        fig.add_trace(go.Scatter(x=ind["adx"].index, y=ind["adx"], name="ADX", line=dict(color="purple", width=1)), row=row_id, col=1)
        fig.add_shape(type="line", x0=ind["adx"].index[0], y0=25, x1=ind["adx"].index[-1], y1=25, name="Weak Trend", line=dict(color="red", width=1, dash="dash"), row=row_id, col=1)
        fig.add_shape(type="line", x0=ind["adx"].index[0], y0=50, x1=ind["adx"].index[-1], y1=50, name="Strong Trend", line=dict(color="green", width=1, dash="dash"), row=row_id, col=1)
        last_adx = ind["adx"][last_timestamp]
        fig.add_annotation(
            x=ind["adx"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:purple'>ADX: {last_adx:.2f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min, y_max = 0, 100
    elif indicator == "OBV":
        # 添加OBV指标
        fig.add_trace(go.Scatter(x=ind["obv"].index, y=ind["obv"], name="OBV", line=dict(color="blue", width=1)), row=row_id, col=1)
        last_obv = ind["obv"][last_timestamp]
        fig.add_annotation(
            x=ind["obv"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:blue'>OBV: {last_obv:.2f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min = ind["obv"].min()
        y_max = ind["obv"].max()
    elif indicator == "SMA":
        # 添加SMA指标
        fig.add_trace(go.Scatter(x=ind["sma"].index, y=ind["sma"], name="SMA 40", line=dict(color="blue", width=1)), row=row_id, col=1)
        last_sma = ind["sma"][last_timestamp]
        fig.add_annotation(
            x=ind["sma"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:blue'>SMA 40: {last_sma:.4f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min = ind["sma"].min()
        y_max = ind["sma"].max()
    elif indicator == "TEMA":
        # 添加TEMA指标
        fig.add_trace(go.Scatter(x=ind["tema"].index, y=ind["tema"], name="TEMA 9", line=dict(color="blue", width=1)), row=row_id, col=1)
        last_tema = ind["tema"][last_timestamp]
        fig.add_annotation(
            x=ind["tema"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:blue'>TEMA 9: {last_tema:.4f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min = ind["tema"].min()
        y_max = ind["tema"].max()
    elif indicator == "MFI":
        # 添加MFI指标
        fig.add_trace(go.Scatter(x=ind["mfi"].index, y=ind["mfi"], name="MFI", line=dict(color="purple", width=1)), row=row_id, col=1)
        fig.add_shape(type="line", x0=ind["mfi"].index[0], y0=80, x1=ind["mfi"].index[-1], y1=80, name="Overbought", line=dict(color="red", width=1, dash="dash"), row=row_id, col=1)
        fig.add_shape(type="line", x0=ind["mfi"].index[0], y0=20, x1=ind["mfi"].index[-1], y1=20, name="Oversold", line=dict(color="green", width=1, dash="dash"), row=row_id, col=1)
        last_mfi = ind["mfi"][last_timestamp]
        fig.add_annotation(
            x=ind["mfi"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:purple'>MFI: {last_mfi:.2f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min, y_max = 0, 100
    elif indicator == "CCI":
        # 添加CCI指标
        fig.add_trace(go.Scatter(x=ind["cci"].index, y=ind["cci"], name="CCI", line=dict(color="purple", width=1)), row=row_id, col=1)
        fig.add_shape(type="line", x0=ind["cci"].index[0], y0=100, x1=ind["cci"].index[-1], y1=100, name="Overbought", line=dict(color="red", width=1, dash="dash"), row=row_id, col=1)
        fig.add_shape(type="line", x0=ind["cci"].index[0], y0=-100, x1=ind["cci"].index[-1], y1=-100, name="Oversold", line=dict(color="green", width=1, dash="dash"), row=row_id, col=1)
        last_cci = ind["cci"][last_timestamp]
        fig.add_annotation(
            x=ind["cci"].index[0],  # 左上角位置
            y=1.0,
            text=f"<span style='color:purple'>CCI: {last_cci:.2f}</span>",
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(0, 0, 0, 0)",
            bordercolor="rgba(0, 0, 0, 1)",
            xref=f"x{row_id}",
            yref=f"y{row_id} domain" if row_id > 1 else f"y domain",
            align="left",
            xanchor="left",
            yanchor="top",
        )
        y_min, y_max = -200, 200
    else:
        raise ValueError(f"Unsupported indicator: {indicator}")
    return fig, (y_min, y_max)


def add_position_price_line_to_figure(
    fig: go.Figure,
    row_id: int,
    name: str,
    price: float,
    amount: float,
    position_side: str,
    start_time: pd.Timestamp,
    end_time: pd.Timestamp,
    color=None,
    marker=None,
    suffix=None,
) -> go.Figure:
    """
    在图表中添加价格水平线

    Args:
        fig (go.Figure): Plotly 图表对象
        row_id (int): 行号
        name (str): 价格水平线名称
        price (float): 价格水平
        amount (float): 交易数量
        position_side (str): 交易方向，"long" 或 "short"
        start_time (pd.Timestamp): 开始时间戳
        end_time (pd.Timestamp): 结束时间戳
        color (str): 线条颜色
        marker (str): 价格标注符号
        suffix (str): 价格标注后缀

    Returns:
        go.Figure: 更新后的图表对象
    """
    price = float(price)
    amount = float(amount)
    position_side = position_side.lower()
    assert position_side in ["long", "short"], "Position side must be 'long' or 'short'"
    if not color:
        color = "green" if position_side == "long" else "red"
    if amount == 0:
        text = f"{price}"
    else:
        if not marker:
            marker = "▲" if position_side == "long" else "▼"
        text = f"{marker} {price} ({abs(amount)})"
        if suffix:
            text += f" {suffix}"

    # 添加横线
    fig.add_trace(
        go.Scatter(
            x=[start_time, end_time],
            y=[price, price],
            mode="lines",
            line=dict(color=color, width=1, dash="dash"),
            showlegend=True,
            legendgroup=name,  # 使用传入的 name 进行分组
            legendgrouptitle_text=name,  # 设置图例组的标题
            name=text,  # 使用标注的 text 作为此线条在图例中的名称
        ),
        row=row_id,
        col=1,
    )

    # 添加价格标注
    fig.add_annotation(
        name=name,
        x=start_time,
        y=price,
        text=text.replace("<br>", ""),
        showarrow=False,
        font=dict(size=10, color="white"),
        bgcolor=color,
        bordercolor="rgba(0, 0, 0, 0)",
        xref="x1",
        yref="y" if row_id == 1 else f"y{row_id}",
        align="left" if position_side == "long" else "right",
        # yshift=6 if position_side == "long" else -6,  # 上方或下方偏移
        yshift=0,  # 上方或下方偏移
        xanchor="left",
        yanchor="bottom" if position_side == "long" else "top",
        xshift=0,
    )
    return fig


def add_position_price_line_to_figure2(
    fig: go.Figure,
    row_id: int,
    name: str,  # 用于 legendgroup 和 legendgrouptitle_text，如图例组的名称
    price: float,
    amount: float,
    position_side: str,
    start_time: pd.Timestamp,
    end_time: pd.Timestamp,
    color=None,
    marker=None,
    suffix=None,
) -> go.Figure:
    """
    在图表中添加价格水平线和文本标注，文本标注的显隐与线条同步。

    Args:
        fig (go.Figure): Plotly 图表对象
        row_id (int): 行号
        name (str): 此价格水平线的逻辑名称，用于图例分组 (e.g., "持仓成本线")
        price (float): 价格水平
        amount (float): 交易数量
        position_side (str): 交易方向，"long" 或 "short"
        start_time (pd.Timestamp): 开始时间戳
        end_time (pd.Timestamp): 结束时间戳
        color (str): 线条和文本背景颜色
        marker (str): 价格标注符号
        suffix (str): 价格标注后缀

    Returns:
        go.Figure: 更新后的图表对象
    """
    price = float(price)
    amount = float(amount)
    position_side = position_side.lower()
    assert position_side in ["long", "short"], "Position side must be 'long' or 'short'"

    if not color:
        color = "green" if position_side == "long" else "red"

    # 构建文本内容
    text_content = ""
    if amount == 0:
        text_content = f"{price:.2f}"  # Ensure price is formatted
    else:
        if not marker:
            marker = "▲" if position_side == "long" else "▼"
        text_content = f"{marker} {price:.2f} ({abs(amount)})"
        if suffix:
            text_content += f" {suffix}"
    print(position_side, marker, text_content)

    # 使用 HTML 设置文本样式 (背景色、文字颜色等)
    html_styled_text = f"""<span style="color:{color}; font-size:9px;">{text_content}</span>"""

    # 根据 position_side 确定 textposition，以模拟原 annotation 的 yshift
    # 原 annotation: xanchor='left', yanchor='middle', xshift=0
    # yshift > 0 (long) 文本在价格线上方; yshift < 0 (short) 文本在价格线下方
    if position_side == "long":
        # 文本底部左侧与 (start_time, price)对齐，使文本显示在价格线上方
        scatter_textposition = "bottom right"
    else:  # position_side == "short"
        # 文本顶部左侧与 (start_time, price)对齐，使文本显示在价格线下方
        scatter_textposition = "top right"

    x = pd.date_range(start=start_time, end=end_time, freq="1min")
    y = [price] * len(x)

    fig.add_trace(
        go.Scatter(
            # x=[start_time, end_time],
            # y=[price, price],
            x=x,
            y=y,
            mode="lines+text",  # 同时显示线条和文本
            line=dict(color=color, width=1, dash="dash"),
            text=[""] + [html_styled_text] + [""] * (len(x) - 2),  # 文本仅在第一个点(start_time)显示
            textposition=scatter_textposition,
            # textpositionsrc="y",  # 确保文本位置与 y 轴对齐
            hoverinfo="none",  # 可以设置为 'x+y+text' 或 'none' 等
            showlegend=True,
            legendgroup=name,  # 图例分组的名称
            legendgrouptitle_text=name,  # 图例分组的标题
            name=text_content,  # 此轨迹在图例中的名称为实际的文本内容
        ),
        row=row_id,
        col=1,
    )

    return fig


def add_order_price_line_to_figure(
    fig: go.Figure,
    row_id: int,
    price: float,
    amount: float,
    order_type: str,
    start_time: pd.Timestamp,
    end_time: pd.Timestamp,
    color: str = None,
    marker: str = None,
):
    if not color:
        color = "green" if order_type == "BUY" else "red"
    if not marker:
        marker = "▲" if order_type == "BUY" else "▼"
    amount = float(amount)
    if amount == 0:
        text = f"{price}"
    else:
        text = f"{marker} {price} ({abs(amount)})"

    # 添加横线
    fig.add_shape(
        type="line",
        x0=start_time,
        y0=price,
        x1=end_time,
        y1=price,
        line=dict(color=color, width=1, dash="dash"),
        row=row_id,
        col=1,
    )

    # 添加价格标注
    fig.add_annotation(
        x=end_time,
        y=price,
        text=text,
        showarrow=False,
        font=dict(size=10, color="white"),
        bgcolor=color,
        bordercolor="rgba(0, 0, 0, 0)",
        xref="x1",
        yref="y" if row_id == 1 else f"y{row_id}",
        align="left" if order_type == "BUY" else "right",
        yshift=5 if order_type == "BUY" else -5,  # 上方或下方偏移
        xanchor="left",
        yanchor="middle",
        xshift=0,
    )
    return fig


def add_time_separator(
    fig: go.Figure,
    row_id: int,
    last_timestamp: pd.Timestamp,
    y_min: float,
    y_max: float,
) -> go.Figure:
    """
    在图表中添加时间分割线

    Args:
        fig (go.Figure): Plotly 图表对象
        row_id (int): 分割线所在的行号
        last_timestamp (pd.Timestamp): 分割线的时间戳
        y_min (float): 分割线的最小y值
        y_max (float): 分割线的最大y值

    Returns:
        go.Figure: 更新后的图表对象
    """
    # 使用正确的yref格式: y, y2, y3
    yref = f"y{row_id}" if row_id > 1 else "y"
    yref_anno = f"y{row_id} domain" if row_id > 1 else "y domain"

    # 添加垂直线
    fig.add_shape(
        type="line",
        x0=last_timestamp,
        y0=y_min,
        x1=last_timestamp,
        y1=y_max,
        line=dict(color="black", width=2, dash="dash"),
        xref=f"x{row_id}",
        yref=yref,
    )

    # 添加分割线标签
    fig.add_annotation(
        x=last_timestamp,
        y=1.05,
        text="<- History  |  Future ->",
        showarrow=False,
        font=dict(size=12, color="black"),
        xref=f"x{row_id}",
        yref=yref_anno,
    )

    return fig


def add_volume_bar_to_figure(
    fig: go.Figure,
    row_id: int,
    df: pd.DataFrame,
    last_timestamp: pd.Timestamp,
    name: str = "Volume",
) -> go.Figure:
    """
    在图表中添加成交量柱状图

    Args:
        fig (go.Figure): Plotly 图表对象
        row_id (int): 行号
        df (pd.DataFrame): 包含成交量数据的 DataFrame，必须包含 "volume", "open", "close" 列
        last_timestamp (pd.Timestamp): 最后一个时间戳，用于添加时间分隔线
        name (str): 图例名称

    Returns:
        go.Figure: 更新后的图表对象
    """
    colors = ["green" if (row["close"] - row["open"]) >= 0 else "red" for i, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df["volume"], name=name, marker_color=colors), row=row_id, col=1)
    y_min, y_max = 0, df["volume"].max() * 1.1
    fig = add_time_separator(fig, row_id, last_timestamp, y_min, y_max)
    last_volume = df["volume"].iloc[-1]
    fig.add_annotation(
        x=df.index[0],  # 左上角位置
        y=1.0,
        text=f"<span style='color:{'green' if last_volume >= 0 else 'red'}'>Volume: {last_volume:.2f}</span>",
        showarrow=False,
        font=dict(size=12),
        bgcolor="rgba(0, 0, 0, 0)",
        bordercolor="rgba(0, 0, 0, 1)",
        xref=f"x{row_id}",
        yref=f"y{row_id} domain",
        align="left",
        xanchor="left",
        yanchor="top",
    )
    return fig


class OrderConfig(TypedDict):
    price: float  # 价格
    amount: float  # 数量
    side: Literal["BUY", "SELL"]  # 订单方向


class PositionConfig(TypedDict):
    price: float  # 价格
    amount: float  # 数量
    side: Literal["long", "short"]  # 持仓方向
    start_time: str  # 开始时间，格式为 "YYYY-MM-DD HH:MM:SS"
    end_time: str | None  # 结束时间，格式为 "YYYY-MM-DD HH:MM:SS"，如果没有则为 None
    stop_loss_price: float | None  # 止损价格，如果没有则为 None
    take_profit_price: float | None  # 止盈价格，如果没有则为 None


class PredictionConfig(TypedDict):
    date: str  # 预测日期，格式为 "YYYY-MM-DD"
    price: float  # 预测价格


IndicatorType = Literal["BB", "Trend", "EMA", "MACD", "RSI", "SMA", "TEMA", "ATR", "STOCH", "ADX", "OBV", "MFI", "CCI"]


class FigureConfig(TypedDict):
    symbol: str  # 交易对
    freq: Literal["1m", "5m", "15m", "1d"]  # 数据频率
    lookback: int  # 回看窗口大小，单位为 $freq

    title: str  # 图表标题
    primary_indicators: Optional[IndicatorType]  # 主图指标
    secondary_indicators: list[IndicatorType]  # 副图指标
    show_volume: bool  # 是否显示成交量

    drawing_code: str  # 绘图代码

    show_time_separator: bool  # 是否显示分割过去和未来的时间分隔线
    predictions: list[PredictionConfig]  # 价格预测

    orders: list[OrderConfig]  # 订单列表
    positions: list[PositionConfig]  # 持仓列表


def convert_freq(freq_str: str):
    """
    将时间频率字符串转换为Pandas DataFrame可用的格式

    参数:
        freq_str (str): 时间频率字符串，如 '5m', '1h', '1d'

    返回:
        str: 转换后的频率字符串，如 '5min', '1h', '1D'
    """
    # 去除空格并转换为小写
    freq_str = freq_str.strip().lower()

    # 常见的转换映射
    replacements = {
        "m": "min",  # 分钟
        "h": "h",  # 小时 (保持不变)
        "d": "d",  # 天 (通常需要大写，但我们在最后处理)
        "w": "w",  # 周 (保持不变)
        "mon": "b",  # 工作日
        "y": "a",  # 年
        "q": "q",  # 季度
        "s": "s",  # 秒
        "ms": "ms",  # 毫秒
    }

    # 处理数字和单位分离的情况
    for unit, replacement in replacements.items():
        if freq_str.endswith(unit):
            # 替换单位部分，保留数字
            return freq_str.replace(unit, replacement).upper()

    # 如果没有匹配的单位，返回原字符串
    return freq_str


def interpolated_predictions(predictions: list[dict], freq="1d", method="quadratic"):
    """
    以指定频率对时间序列进行插值

    参数:
    df: 包含时间序列数据的DataFrame
    freq: 频率字符串，如'1m'(1分钟)、'5m'(5分钟)、'1h'(1小时)、'1d'(1天)
    method: 插值方法，如'linear'(线性)、'quadratic'(二次)、'cubic'(三次)等

    返回:
    插值后的pd.Series，索引为pd.Timestamp
    """
    # print(predictions)
    freq = convert_freq(freq)
    # 转换为DataFrame
    df = pd.DataFrame(predictions)

    # 将date列转换为datetime类型并设置为索引
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    # 检查索引是否有重复值
    if df.index.duplicated().any():
        # 删除重复索引
        df = df[~df.index.duplicated()]
        # # 聚合重复索引（例如取平均值）
        # df = df.groupby(df.index).mean()
    # 创建完整的时间范围索引
    full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq=freq)

    # 用 reindex 显式补全缺失时间点
    df = df.reindex(full_index)

    # 使用指定方法进行插值
    df = df.interpolate(method=method)

    # 转换为Series
    return df["price"]


def plot_figure_from_config(
    config: FigureConfig,
    fetch_data: Callable[[str, str, int], tuple[pd.Timestamp, float, pd.DataFrame]],
) -> go.Figure:
    """
    绘制K线图并标注止损、止盈以及价格预测

    Args:
        config (FigureConfig): 图表配置

    Returns:
        fig (plotly.graph_objects.Figure): K线图
    """
    symbol: str = config["symbol"]
    lookback: int = config["lookback"]
    freq: Literal["1m", "5m", "15m", "1d"] = config["freq"]
    title: str = config["title"]
    show_volume: bool = config["show_volume"]
    show_time_separator: bool = config["show_time_separator"]
    drawing_code: str = config["drawing_code"]
    primary_indicator: Optional[str] = config["primary_indicator"]
    secondary_indicators: list[str] = config["secondary_indicators"]

    positions: list[PositionConfig] = config["positions"]
    orders: list[OrderConfig] = config["orders"]
    predictions: list[PredictionConfig] = config["predictions"]

    current_datetime, current_price, df = fetch_data(symbol, freq, lookback)
    if not primary_indicator:
        primary_indicator = "BB"
    indicators: list[str] = [primary_indicator] + secondary_indicators

    predicted_close: Optional[pd.Series] = None
    # 拼接预测的收盘价
    close = df["close"]
    assert len(close) > 2, "Close price series is too short"
    concat_close = close.copy()
    if len(predictions) > 0:
        # 如果有预测数据，进行插值
        predicted_close = interpolated_predictions([{"date": df.index[-1], "price": close.iloc[-1]}] + predictions, freq=freq)
        print(predicted_close)
        if predicted_close.empty:
            raise ValueError("Predicted close series is empty after interpolation")
        concat_close = pd.concat([close, predicted_close], ignore_index=False)
        if concat_close.index.duplicated().any():
            # 删除重复索引
            concat_close = concat_close[~concat_close.index.duplicated()]
    ind = indicators_from_close(concat_close)

    ind: dict[str, pd.Series] = {}
    ind1 = indicators_from_close(concat_close, indicators)
    ind1["index"] = concat_close.index
    for name, series in ind1.items():
        ind1[name] = series[-lookback - len(predicted_close) :] if predicted_close is not None else series[-lookback:]
    ind.update(ind1)
    # volume 和 high low 不能预测
    ind2 = indicators_from_close_volume_high_low(df["close"], df["volume"], df["high"], df["low"], indicators)
    for name, series in ind2.items():
        ind2[name] = series[-lookback:]
    ind.update(ind2)

    concat_close = concat_close[-lookback - len(predicted_close) :] if predicted_close is not None else concat_close[-lookback:]
    df = df.iloc[-lookback:]
    last_timestamp = df.index[-1]

    valid_secondary_indicators = [indicator for indicator in secondary_indicators if indicator in available_indicators]
    subplot_titles = ["K Line"]
    total_rows = 1
    row_heights = [0.8]
    height = 400
    if show_volume:
        subplot_titles.append("Volume")
        total_rows += 1
        row_heights.append(0.2)
        height += 200

    for name in valid_secondary_indicators:
        subplot_titles.append(name)
        total_rows += 1
        row_heights.append(0.2)
        height += 200
    # K线图 + Volume + 每个指标一行

    fig = make_subplots(
        subplot_titles=subplot_titles,
        rows=total_rows,
        cols=1,
        row_heights=row_heights,
        shared_xaxes=True,
        vertical_spacing=0.05,
    )

    # 添加K线图 (绿色代表上涨, 红色代表下跌)
    row_id = 1
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="1min kline",
            increasing_line_color="green",  # 上涨为绿色
            decreasing_line_color="red",  # 下跌为红色
        ),
        row=row_id,
        col=1,
    )

    # 添加价格预测数据
    if len(predictions) > 0:
        fig.add_trace(go.Scatter(x=predicted_close.index, y=predicted_close, mode="lines", name="predicted_close", line=dict(color="blue", width=3)), row=row_id, col=1)
        fig.add_trace(go.Scatter(x=predicted_close.index, y=predicted_close, mode="markers", name="predicted_close", marker=dict(color="blue", size=5)), row=row_id, col=1)

    # 添加订单价格横线和标注
    if len(orders) > 0:
        for order in orders:
            order_price = float(order["price"])
            if order_price < concat_close.min() or order_price > concat_close.max():
                # 如果开仓价格不在当前收盘价范围内，跳过该持仓
                continue
            fig = add_order_price_line_to_figure(
                fig,
                row_id,
                order["price"],
                order["amount"],
                order["side"],
                df.index[0],
                concat_close.index[-1],
            )

    # 添加持仓标记
    if len(positions) > 0:
        for position in positions:
            if float(position["amount"]) == 0:
                continue  # 跳过空仓
            entry_price = float(position["price"])
            if entry_price <= 0:
                # 如果开仓价格为0或负数，跳过该持仓
                continue
            if entry_price < concat_close.min() or entry_price > concat_close.max():
                # 如果开仓价格不在当前收盘价范围内，跳过该持仓
                continue
            position_amt = float(position["amount"])
            position_side = position["side"]
            name = f"{position_side} Position"
            fig = add_position_price_line_to_figure(
                fig,
                row_id,
                name,
                entry_price,
                position_amt,
                position_side,
                df.index[0],
                concat_close.index[-1],
                marker=("▲" if position_side.lower() == "long" else "▼") + "持仓价",
            )

    # 添加当前价格水平线
    fig = add_order_price_line_to_figure(
        fig,
        row_id,
        current_price,
        0,
        "BUY",
        last_timestamp,
        concat_close.index[-1],
        color="black",
    )
    # 添加主图技术指标 (主图只能加 1 个指标)
    main_y_min, main_y_max = concat_close.min(), concat_close.max()
    fig, (y_min, y_max) = add_indicators_to_figure(fig, row_id, primary_indicator, ind, last_timestamp)
    main_y_min = min(main_y_min, y_min)
    main_y_max = max(main_y_max, y_max)

    if show_time_separator:
        fig = add_time_separator(fig, 1, last_timestamp, main_y_min, main_y_max)
    # fig.add_annotation(
    #     x=df.index[0],  # 左上角位置
    #     y=1.0,
    #     text=f"<span style='color:black'>Time: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}</span>  <span style='color:{'green' if (current_price - df['close'].iloc[-1]) >= 0 else 'red'}'>Price: {current_price:.2f}</span>",
    #     showarrow=False,
    #     font=dict(size=12),
    #     bgcolor="rgba(0, 0, 0, 0)",
    #     bordercolor="rgba(0, 0, 0, 1)",
    #     xref=f"x{row_id}",
    #     yref=f"y domain",
    #     align="left",
    #     xanchor="left",
    #     yanchor="top",
    # )

    # 添加成交量图
    if show_volume:
        row_id += 1
        fig = add_volume_bar_to_figure(fig, row_id, df, last_timestamp, name="Volume")

    # 添加技术指标
    yaxis_kwargs = {}
    if show_volume:
        yaxis2 = dict(
            title="Volume",
            showticklabels=True,
        )
        yaxis_kwargs["yaxis2"] = yaxis2
    for indicator in valid_secondary_indicators:
        row_id += 1
        fig, (y_min, y_max) = add_indicators_to_figure(fig, row_id, indicator, ind, last_timestamp)
        if show_time_separator:
            fig = add_time_separator(fig, row_id, last_timestamp, y_min, y_max)
        yaxis_kwargs[f"yaxis{row_id}"] = dict(
            title=indicator,
            range=[y_min, y_max],
            showticklabels=True,
        )

    # 设置图表布局
    fig.update_layout(
        width=800,
        height=height,
        title=title,
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            # title="Time",
            showticklabels=True,
            # tickformat="%Y-%m-%d %H:%M:%S",  # 时间格式
        ),
        yaxis=dict(
            title="Price",
            tickformat=".0f",  # 保留小数，可根据需要调整
            showexponent="none",  # 不显示指数
            tickmode="auto",  # 自动确定刻度
            showticklabels=True,
        ),
        **yaxis_kwargs,
    )

    # 更新x轴和y轴
    fig.update_xaxes(showticklabels=True, row=total_rows, col=1)
    return fig
