import pandas as pd


def ma_crossover_position(df, short_window=20, long_window=50):
    short_ma = df["Close"].rolling(short_window).mean()
    long_ma = df["Close"].rolling(long_window).mean()

    return (short_ma > long_ma).astype(float)


def rsi_mean_reversion_position(df, entry_level=30, exit_level=50):
    rsi_series = df["RSI_14"]

    position = pd.Series(0.0, index=df.index)
    in_trade = False

    for i in range(len(df)):
        value = rsi_series.iloc[i]

        if pd.isna(value):
            continue

        if not in_trade and value < entry_level:
            in_trade = True
        elif in_trade and value > exit_level:
            in_trade = False

        position.iloc[i] = 1.0 if in_trade else 0.0

    return position


def momentum_position(df, lookback=60):
    momentum = df["Close"].pct_change(lookback)
    return (momentum > 0).astype(float)
