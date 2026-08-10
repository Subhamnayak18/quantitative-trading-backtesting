import matplotlib.pyplot as plt


def save_equity_curve(benchmark, backtests, path):
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        benchmark.index,
        benchmark["equity_curve"],
        label="Buy & Hold",
        linewidth=1.4,
    )

    for name, result in backtests.items():
        ax.plot(
            result.index,
            result["equity_curve"],
            label=name,
            linewidth=1.1,
        )

    ax.set_title("Strategy Equity Curves vs NIFTY 50 Buy & Hold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth of 1 unit")
    ax.legend()
    ax.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def save_drawdown_comparison(benchmark, backtests, path):
    fig, ax = plt.subplots(figsize=(12, 5))

    benchmark_dd = (
        benchmark["equity_curve"]
        / benchmark["equity_curve"].cummax()
        - 1
    )
    ax.plot(
        benchmark.index,
        benchmark_dd,
        label="Buy & Hold",
        linewidth=1.2,
    )

    for name, result in backtests.items():
        dd = (
            result["equity_curve"]
            / result["equity_curve"].cummax()
            - 1
        )
        ax.plot(result.index, dd, label=name, linewidth=1.0)

    ax.set_title("Drawdown Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.legend()
    ax.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def save_market_overview(market, path):
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        market.index,
        market["Close"],
        label="NIFTY 50",
        linewidth=1.2,
    )
    ax.plot(
        market.index,
        market["SMA_20"],
        label="SMA 20",
        linewidth=1.0,
    )
    ax.plot(
        market.index,
        market["SMA_50"],
        label="SMA 50",
        linewidth=1.0,
    )

    ax.set_title("NIFTY 50 Market Overview")
    ax.set_xlabel("Date")
    ax.set_ylabel("Index Level")
    ax.legend()
    ax.grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
