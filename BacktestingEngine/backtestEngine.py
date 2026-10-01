from logging_config import get_logger
from BacktestingEngine.performanceMetrics import PerformanceMetrics
from BacktestingEngine.positionSizer import FixedSharesPositionSizer
from typing import Optional

logger = get_logger(__name__)


class BacktestEngine:
    """
    Backtesting engine that simulates trading based on signals.

    Maintains portfolio state, executes trades based on signals, and calculates
    performance metrics. Includes optional stop-loss and take-profit exit logic.
    """

    def __init__(
        self,
        initial_cash: float = 100000.0,
        position_sizer=None,
        commission: float = 0.001,
        slippage: float = 0.0005,
        stop_loss_pct: float = 0.05,
        take_profit_pct: float = 0.10,
    ):
        """
        Initialize the backtest engine.

        Args:
            initial_cash: Starting cash for portfolio.
            position_sizer: PositionSizer instance for calculating trade sizes.
            commission: Commission per trade as a fraction.
            slippage: Slippage per trade as a fraction.
            stop_loss_pct: Stop loss threshold as a decimal.
            take_profit_pct: Take profit threshold as a decimal.
        """
        self.initial_cash = initial_cash
        self.position_sizer = position_sizer or FixedSharesPositionSizer(1)
        self.commission = commission
        self.slippage = slippage
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trades = []
        self.entry_price: Optional[float] = None
        self.position_size = 0

        logger.info(
            "Initialized BacktestEngine: initial_cash=%s, position_sizer=%s, "
            "commission=%s%%, slippage=%s%%, stop_loss=%s%%, take_profit=%s%%",
            initial_cash,
            type(self.position_sizer).__name__,
            commission * 100,
            slippage * 100,
            stop_loss_pct * 100,
            take_profit_pct * 100,
        )

    def run_backtest(self, data, signals):
        """
        Run the backtest simulation.

        Args:
            data: DataFrame with OHLCV data.
            signals: Series of trading signals (1=buy, -1=sell, 0=hold).

        Returns:
            PerformanceMetrics object containing portfolio statistics.

        Raises:
            ValueError: If data or signals are invalid.
        """
        if data is None or signals is None or len(data) == 0:
            raise ValueError("Data and signals cannot be empty")

        if len(data) != len(signals):
            raise ValueError("Data and signals must have same length")

        if 'open' not in data.columns or 'close' not in data.columns:
            raise ValueError("Data must contain 'open' and 'close' columns")

        logger.info(
            "Starting backtest with %s rows and initial cash %s",
            len(data),
            self.initial_cash,
        )

        portfolio_values = [self.initial_cash]
        cash = self.initial_cash
        position_size = 0
        self.entry_price = None
        self.trades = []

        for i in range(1, len(data)):
            signal = signals.iloc[i - 1]
            current_price = float(data['open'].iloc[i])
            close_price = float(data['close'].iloc[i])
            account_value = cash + position_size * current_price

            def exit_position(reason: str) -> None:
                nonlocal cash, position_size
                slipped_exit_price = current_price * (1 - self.slippage)
                trade_revenue = position_size * slipped_exit_price
                commission_cost = trade_revenue * self.commission
                net_revenue = trade_revenue - commission_cost
                profit = net_revenue - (position_size * self.entry_price)
                cash += net_revenue

                trade = {
                    'entry_date': data.index[i - 1] if hasattr(data, 'index') else i - 1,
                    'entry_price': self.entry_price,
                    'exit_date': data.index[i] if hasattr(data, 'index') else i,
                    'exit_price': slipped_exit_price,
                    'profit': profit,
                    'shares': position_size,
                    'return_pct': (profit / (position_size * self.entry_price) * 100) if self.entry_price else 0,
                    'exit_reason': reason,
                }
                self.trades.append(trade)
                logger.debug(
                    "SELL (%s): %s shares at $%.2f (slipped: $%.2f) on row %s "
                    "(profit: $%.2f, commission: $%.2f)",
                    reason,
                    position_size,
                    current_price,
                    slipped_exit_price,
                    i,
                    profit,
                    commission_cost,
                )
                position_size = 0
                self.entry_price = None

            if signal == 1 and position_size == 0:
                shares_to_buy = self.position_sizer.calculate_position_size(
                    account_value=account_value,
                    current_price=current_price,
                    stop_loss_pct=self.stop_loss_pct,
                )

                if shares_to_buy > 0:
                    slipped_price = current_price * (1 + self.slippage)
                    trade_cost = shares_to_buy * slipped_price
                    commission_cost = trade_cost * self.commission
                    total_cost = trade_cost + commission_cost

                    if cash >= total_cost:
                        position_size = shares_to_buy
                        cash -= total_cost
                        self.entry_price = slipped_price

                        logger.debug(
                            "BUY: %s shares at $%.2f (slipped: $%.2f) on row %s "
                            "(cost: $%.2f, commission: $%.2f)",
                            shares_to_buy,
                            current_price,
                            slipped_price,
                            i,
                            trade_cost,
                            commission_cost,
                        )

            elif position_size > 0:
                unrealized_return_pct = (current_price - self.entry_price) / self.entry_price
                if unrealized_return_pct <= -self.stop_loss_pct:
                    exit_position('stop_loss')
                elif unrealized_return_pct >= self.take_profit_pct:
                    exit_position('take_profit')
                elif signal == -1:
                    exit_position('signal_exit')

            portfolio_values.append(cash + position_size * close_price)

        logger.info(
            "Backtest complete. Final portfolio value: %.2f, Trades executed: %s",
            portfolio_values[-1],
            len(self.trades),
        )

        return PerformanceMetrics(portfolio_values, self.trades)
