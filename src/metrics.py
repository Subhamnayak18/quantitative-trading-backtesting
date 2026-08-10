import numpy as np
import pandas as pd


def max_drawdown_from_returns(returns):
    equity = (1 + returns.fillna(0.0)).cumprod()
    peak = equity.cummax()
    return (equity / peak - 1).min()


def trade_returns(backtest_df):
    position = backtest_df["position"]
    net_return = backtest_df["net_return"]

    entries = (position == 1) & (
        position.shift(1, fill_value=0) == 0
    )
    exits = (position == 0) & (
        position.shift(1, fill_value=0) == 1
    )

    entry_idx = list(np.flatnonzero(entries.to_numpy()))
    exit_idx = list(np.flatnonzero(exits.to_numpy()))

    trades = []

    for start in entry_idx:
        matching_exits = [idx for idx in exit_idx if idx > start]
        end = matching_exits[0] if matching_exits else len(backtest_df) - 1

        # Include exit day so its transaction cost belongs to the trade.
        r = net_return.iloc[start:end + 1]
        trades.append((1 + r).prod() - 1)

    return pd.Series(trades, dtype=float)


def performance_metrics(
    returns,
    backtest_df=None,
    trading_days=252,
):
    returns = returns.fillna(0.0)

    total_return = (1 + returns).prod() - 1
    years = len(returns) / trading_days

    cagr = (
        (1 + total_return) ** (1 / years) - 1
        if years > 0 else np.nan
    )

    annual_vol = returns.std(ddof=1) * np.sqrt(trading_days)
    annual_return = returns.mean() * trading_days

    sharpe = (
        annual_return / annual_vol
        if annual_vol > 0 else np.nan
    )

    max_dd = max_drawdown_from_returns(returns)
    calmar = cagr / abs(max_dd) if max_dd < 0 else np.nan

    metrics = {
        "Total Return": total_return,
        "CAGR": cagr,
        "Annualized Volatility": annual_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd,
        "Calmar Ratio": calmar,
    }

    if backtest_df is not None:
        trades = trade_returns(backtest_df)
        winners = trades[trades > 0]
        losers = trades[trades < 0]

        metrics.update({
            "Number of Trades": int(len(trades)),
            "Win Rate": (
                (trades > 0).mean()
                if len(trades) else np.nan
            ),
            "Average Trade Return": (
                trades.mean()
                if len(trades) else np.nan
            ),
            "Average Winner": (
                winners.mean()
                if len(winners) else np.nan
            ),
            "Average Loser": (
                losers.mean()
                if len(losers) else np.nan
            ),
            "Profit Factor": (
                winners.sum() / abs(losers.sum())
                if len(losers) and losers.sum() != 0
                else np.nan
            ),
        })

    return metrics
