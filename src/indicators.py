import numpy as np


def sma(series, window):
    return series.rolling(window=window, min_periods=window).mean()


def rsi(series, window=14):
    change = series.diff()

    gains = change.clip(lower=0)
    losses = -change.clip(upper=0)

    avg_gain = gains.ewm(
        alpha=1 / window,
        adjust=False,
        min_periods=window,
    ).mean()

    avg_loss = losses.ewm(
        alpha=1 / window,
        adjust=False,
        min_periods=window,
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    value = 100 - (100 / (1 + rs))
    value = value.where(avg_loss != 0, 100.0)

    return value


def rolling_volatility(returns, window=20, trading_days=252):
    return returns.rolling(
        window=window,
        min_periods=window,
    ).std() * np.sqrt(trading_days)


def drawdown_from_price(series):
    peak = series.cummax()
    return series / peak - 1


def add_features(market, trading_days=252):
    df = market.copy()

    df["Daily_Return"] = df["Close"].pct_change()
    df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))
    df["Cumulative_Return"] = (
        1 + df["Daily_Return"].fillna(0)
    ).cumprod() - 1

    df["SMA_20"] = sma(df["Close"], 20)
    df["SMA_50"] = sma(df["Close"], 50)
    df["SMA_200"] = sma(df["Close"], 200)

    df["RSI_14"] = rsi(df["Close"], 14)
    df["Momentum_20"] = df["Close"].pct_change(20)
    df["Rolling_Volatility_20"] = rolling_volatility(
        df["Daily_Return"], 20, trading_days
    )

    df["Rolling_Max"] = df["Close"].cummax()
    df["Drawdown"] = drawdown_from_price(df["Close"])

    return df
