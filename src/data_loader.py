import pandas as pd
import yfinance as yf

from .config import DATA_PATH, RAW_DATA_DIR


def download_market_data(ticker, start_date, end_date):
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    data = yf.Ticker(ticker).history(
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        actions=False,
    )

    if data.empty:
        raise RuntimeError("No market data was returned.")

    wanted = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    data = data[[c for c in wanted if c in data.columns]].copy()

    data.index = pd.to_datetime(data.index)
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    data.index.name = "Date"
    data = data.sort_index()
    data.to_csv(DATA_PATH)

    return data


def validate_and_clean(data):
    price_cols = ["Open", "High", "Low", "Close"]

    if data.index.duplicated().any():
        data = data[~data.index.duplicated(keep="first")]

    data = data.dropna(subset=price_cols).copy()

    if (data[price_cols] <= 0).any().any():
        raise ValueError("Non-positive OHLC prices found.")

    if (data["High"] < data["Low"]).any():
        raise ValueError("Found rows where High < Low.")

    if (data["High"] < data[["Open", "Close"]].max(axis=1)).any():
        raise ValueError("Found rows where High is below Open or Close.")

    if (data["Low"] > data[["Open", "Close"]].min(axis=1)).any():
        raise ValueError("Found rows where Low is above Open or Close.")

    return data
