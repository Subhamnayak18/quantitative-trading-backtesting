from pathlib import Path

TICKER = "^NSEI"
START_DATE = "2015-01-01"
END_DATE = "2026-08-11"   # yfinance end date is exclusive

TRANSACTION_COST = 0.0005
TRADING_DAYS = 252

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RESULTS_DIR = PROJECT_ROOT / "results"
IMAGES_DIR = PROJECT_ROOT / "images"

DATA_PATH = RAW_DATA_DIR / "nifty50_daily.csv"
