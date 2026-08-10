import numpy as np
import pandas as pd


def classify_regime(market):
    distance = market["Close"] / market["SMA_200"] - 1

    regime = pd.Series(
        "Sideways",
        index=market.index,
        dtype="object",
    )

    regime[distance > 0.02] = "Bull"
    regime[distance < -0.02] = "Bear"
    regime[market["SMA_200"].isna()] = np.nan

    # Use yesterday's regime for today's return analysis.
    return regime.shift(1)
