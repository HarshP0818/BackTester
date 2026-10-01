"""
Strategy module for the backtesting engine.

This module defines a strategy abstraction and several concrete strategies. Strategies
generate signals only and do not execute trades.
"""

from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd

from logging_config import get_logger

logger = get_logger(__name__)


class StrategyBase(ABC):
    """Abstract base class for trading strategies."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trade signals from historical price data."""
        pass


class MovingAverageCrossover(StrategyBase):
    """Moving average crossover strategy."""

    def __init__(self, fast_window: int = 20, slow_window: int = 50) -> None:
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        logger.info(
            "Generating MA crossover signals with fast_window=%s slow_window=%s",
            self.fast_window,
            self.slow_window,
        )

        signal = pd.Series(0, index=data.index)
        fast_ma = data['close'].rolling(window=self.fast_window).mean()
        slow_ma = data['close'].rolling(window=self.slow_window).mean()

        signal[fast_ma > slow_ma] = 1
        signal[fast_ma < slow_ma] = -1

        logger.info(
            "Generated %s buy signals and %s sell signals",
            int((signal == 1).sum()),
            int((signal == -1).sum()),
        )
        return signal


class MomentumStrategy(StrategyBase):
    """Momentum strategy that reacts to multi-day price strength."""

    def __init__(self, lookback_period: int = 20, threshold: float = 0.05) -> None:
        self.lookback_period = lookback_period
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        logger.info(
            "Generating momentum signals with lookback=%s threshold=%s",
            self.lookback_period,
            self.threshold,
        )
        signal = pd.Series(0, index=data.index)
        returns = data['close'].pct_change(self.lookback_period)

        signal[returns > self.threshold] = 1
        signal[returns < -self.threshold] = -1

        logger.info(
            "Generated %s momentum buy signals and %s sell signals",
            int((signal == 1).sum()),
            int((signal == -1).sum()),
        )
        return signal


class MeanReversionStrategy(StrategyBase):
    """Mean reversion strategy that trades on deviations from the moving average."""

    def __init__(
        self,
        lookback_period: int = 30,
        std_dev_threshold: float = 2.0,
    ) -> None:
        self.lookback_period = lookback_period
        self.std_dev_threshold = std_dev_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        logger.info(
            "Generating mean reversion signals with lookback=%s threshold=%s",
            self.lookback_period,
            self.std_dev_threshold,
        )
        signal = pd.Series(0, index=data.index)
        rolling_mean = data['close'].rolling(window=self.lookback_period).mean()
        rolling_std = data['close'].rolling(window=self.lookback_period).std()
        z_score = (data['close'] - rolling_mean) / rolling_std

        signal[z_score < -self.std_dev_threshold] = 1
        signal[z_score > self.std_dev_threshold] = -1

        logger.info(
            "Generated %s mean reversion buy signals and %s sell signals",
            int((signal == 1).sum()),
            int((signal == -1).sum()),
        )
        return signal


def create_strategy(config: Dict) -> StrategyBase:
    """Build a strategy instance from configuration."""
    name = config.get('name', 'moving_average_crossover')

    if name == 'moving_average_crossover':
        return MovingAverageCrossover(
            fast_window=int(config.get('fast_window', 20)),
            slow_window=int(config.get('slow_window', 50)),
        )

    if name == 'momentum':
        return MomentumStrategy(
            lookback_period=int(config.get('lookback_period', 20)),
            threshold=float(config.get('threshold', 0.05)),
        )

    if name == 'mean_reversion':
        return MeanReversionStrategy(
            lookback_period=int(config.get('lookback_period', 30)),
            std_dev_threshold=float(config.get('std_dev_threshold', 2.0)),
        )

    logger.warning("Unknown strategy '%s', falling back to moving_average_crossover", name)
    return MovingAverageCrossover()


Strategy = MovingAverageCrossover
