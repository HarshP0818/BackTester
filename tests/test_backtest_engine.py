import pandas as pd
import pytest
from BacktestingEngine.backtestEngine import BacktestEngine
from BacktestingEngine.performanceMetrics import PerformanceMetrics


def test_run_backtest_buy_and_sell_sequence():
    data = pd.DataFrame(
        {
            "open": [10.0, 11.0, 12.0, 13.0, 14.0],
            "close": [10.0, 11.0, 13.0, 14.0, 15.0],
        },
        index=pd.date_range("2020-01-01", periods=5),
    )
    signals = pd.Series([0, 1, 0, -1, 0], index=data.index)

    engine = BacktestEngine(initial_cash=100.0)
    metrics = engine.run_backtest(data, signals)

    assert isinstance(metrics, PerformanceMetrics)
    assert metrics.portfolio_values[0] == pytest.approx(100.0, rel=1e-6)
    assert metrics.portfolio_values[1] == pytest.approx(100.0, rel=1e-6)
    assert metrics.portfolio_values[2] == pytest.approx(100.981994, rel=1e-6)
    assert metrics.portfolio_values[3] == pytest.approx(101.981994, rel=1e-6)
    assert metrics.portfolio_values[4] == pytest.approx(101.961001, rel=1e-6)
