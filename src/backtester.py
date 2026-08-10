import pandas as pd


def run_backtest(market_returns, desired_position, transaction_cost):
    desired_position = desired_position.reindex(
        market_returns.index
    ).fillna(0.0)

    # Today's signal is traded on the next bar.
    position = desired_position.shift(1).fillna(0.0)

    gross_return = position * market_returns.fillna(0.0)

    position_change = position.diff().fillna(position)
    turnover = position_change.abs()

    cost = turnover * transaction_cost
    net_return = gross_return - cost
    equity_curve = (1 + net_return).cumprod()

    return pd.DataFrame({
        "market_return": market_returns,
        "desired_position": desired_position,
        "position": position,
        "position_change": position_change,
        "turnover": turnover,
        "gross_return": gross_return,
        "cost": cost,
        "net_return": net_return,
        "equity_curve": equity_curve,
    })
