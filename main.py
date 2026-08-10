import numpy as np
import pandas as pd

from src.backtester import run_backtest
from src.config import (
    END_DATE,
    IMAGES_DIR,
    RESULTS_DIR,
    START_DATE,
    TICKER,
    TRADING_DAYS,
    TRANSACTION_COST,
)
from src.data_loader import download_market_data, validate_and_clean
from src.indicators import add_features
from src.metrics import performance_metrics
from src.regimes import classify_regime
from src.strategies import (
    ma_crossover_position,
    momentum_position,
    rsi_mean_reversion_position,
)
from src.visualization import (
    save_drawdown_comparison,
    save_equity_curve,
    save_market_overview,
)


def regime_metrics(returns):
    returns = returns.dropna()

    if len(returns) == 0:
        return {
            "Days": 0,
            "Total Return": np.nan,
            "Annualized Return": np.nan,
            "Annualized Volatility": np.nan,
            "Sharpe Ratio": np.nan,
            "Positive Day Rate": np.nan,
        }

    total_return = (1 + returns).prod() - 1
    annual_return = returns.mean() * TRADING_DAYS
    annual_vol = returns.std(ddof=1) * np.sqrt(TRADING_DAYS)
    sharpe = annual_return / annual_vol if annual_vol > 0 else np.nan

    return {
        "Days": len(returns),
        "Total Return": total_return,
        "Annualized Return": annual_return,
        "Annualized Volatility": annual_vol,
        "Sharpe Ratio": sharpe,
        "Positive Day Rate": (returns > 0).mean(),
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading NIFTY 50 data...")
    market = download_market_data(
        TICKER,
        START_DATE,
        END_DATE,
    )

    market = validate_and_clean(market)
    market = add_features(market, TRADING_DAYS)

    print(
        f"Loaded {len(market):,} rows "
        f"from {market.index.min().date()} "
        f"to {market.index.max().date()}."
    )

    positions = {
        "MA Crossover": ma_crossover_position(market, 20, 50),
        "RSI Mean Reversion": rsi_mean_reversion_position(
            market, 30, 50
        ),
        "Momentum": momentum_position(market, 60),
    }

    backtests = {
        name: run_backtest(
            market["Daily_Return"],
            position,
            TRANSACTION_COST,
        )
        for name, position in positions.items()
    }

    benchmark_returns = market["Daily_Return"].fillna(0.0)
    benchmark = pd.DataFrame({
        "net_return": benchmark_returns,
        "equity_curve": (1 + benchmark_returns).cumprod(),
    })

    comparison = {
        "Buy & Hold": performance_metrics(
            benchmark["net_return"],
            trading_days=TRADING_DAYS,
        )
    }

    for name, result in backtests.items():
        comparison[name] = performance_metrics(
            result["net_return"],
            backtest_df=result,
            trading_days=TRADING_DAYS,
        )

    strategy_comparison = pd.DataFrame(comparison).T
    strategy_comparison.to_csv(
        RESULTS_DIR / "strategy_comparison.csv"
    )

    market["Regime"] = classify_regime(market)

    regime_rows = []
    all_returns = {
        "Buy & Hold": benchmark["net_return"],
        **{
            name: result["net_return"]
            for name, result in backtests.items()
        },
    }

    for strategy_name, returns in all_returns.items():
        for regime_name in ["Bull", "Bear", "Sideways"]:
            mask = market["Regime"] == regime_name
            metrics = regime_metrics(returns[mask])

            regime_rows.append({
                "Strategy": strategy_name,
                "Regime": regime_name,
                **metrics,
            })

    pd.DataFrame(regime_rows).to_csv(
        RESULTS_DIR / "regime_performance.csv",
        index=False,
    )

    sensitivity_rows = []

    for short_window in [10, 20, 30]:
        for long_window in [50, 100, 200]:
            position = ma_crossover_position(
                market,
                short_window,
                long_window,
            )

            result = run_backtest(
                market["Daily_Return"],
                position,
                TRANSACTION_COST,
            )

            metrics = performance_metrics(
                result["net_return"],
                backtest_df=result,
                trading_days=TRADING_DAYS,
            )

            sensitivity_rows.append({
                "Short Window": short_window,
                "Long Window": long_window,
                "Total Return": metrics["Total Return"],
                "CAGR": metrics["CAGR"],
                "Sharpe Ratio": metrics["Sharpe Ratio"],
                "Max Drawdown": metrics["Max Drawdown"],
                "Number of Trades": metrics["Number of Trades"],
            })

    pd.DataFrame(sensitivity_rows).to_csv(
        RESULTS_DIR / "parameter_sensitivity.csv",
        index=False,
    )

    cost_rows = []

    for cost_level in [0.0, 0.00025, 0.0005, 0.001]:
        for name, position in positions.items():
            result = run_backtest(
                market["Daily_Return"],
                position,
                cost_level,
            )

            metrics = performance_metrics(
                result["net_return"],
                trading_days=TRADING_DAYS,
            )

            cost_rows.append({
                "Strategy": name,
                "Transaction Cost": cost_level,
                "Total Return": metrics["Total Return"],
                "CAGR": metrics["CAGR"],
                "Sharpe Ratio": metrics["Sharpe Ratio"],
                "Max Drawdown": metrics["Max Drawdown"],
            })

    pd.DataFrame(cost_rows).to_csv(
        RESULTS_DIR / "transaction_cost_sensitivity.csv",
        index=False,
    )

    save_market_overview(
        market,
        IMAGES_DIR / "market_overview.png",
    )
    save_equity_curve(
        benchmark,
        backtests,
        IMAGES_DIR / "equity_curve_comparison.png",
    )
    save_drawdown_comparison(
        benchmark,
        backtests,
        IMAGES_DIR / "drawdown_comparison.png",
    )

    print("\nStrategy comparison:")
    print(
        strategy_comparison[
            [
                "Total Return",
                "CAGR",
                "Sharpe Ratio",
                "Max Drawdown",
                "Number of Trades",
            ]
        ].round(4)
    )

    print("\nCreated result CSVs and charts.")
    print("Project run complete.")


if __name__ == "__main__":
    main()
