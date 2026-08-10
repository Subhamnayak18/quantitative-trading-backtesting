# Data

The project downloads daily NIFTY 50 market data from Yahoo Finance using `yfinance`.

Raw market files are saved under:

```text
data/raw/
```

The raw CSV is intentionally excluded from Git because `main.py` can download and reproduce the dataset automatically.

No synthetic market prices are used.
