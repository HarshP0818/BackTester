# BackTester

BackTester is a modular Python backtesting engine for equities. It combines data loading, validation, storage, strategy evaluation, risk-managed trade execution, and performance analysis into a single workflow.

## Final version highlights

The final version includes:
- YAML-driven configuration for repeatable experiments without changing code
- Multiple position sizing strategies, including fixed percentage, Kelly criterion, fixed shares, and volatility-adjusted sizing
- Strategy abstraction for signal generation and trade decision-making
- Risk controls such as stop-loss and take-profit exits
- Structured logging with console and file output
- PostgreSQL storage with connection pooling and schema resilience
- Performance metrics such as total return, Sharpe ratio, max drawdown, win rate, and profit factor
- Automated tests and Docker support for easier execution

## Optimizations included in the final version

- Added strategic database indexes to accelerate ticker and date-based queries
- Implemented connection pooling to reduce repeated database connection overhead
- Used bulk upserts for faster storage of historical market data
- Added resilient schema handling so older table layouts continue to work
- Centralized configuration to speed up experimentation and reduce code churn
- Added structured logging to make debugging and auditing faster

## Project structure

- `config.py`: centralized YAML configuration loader with dot-path access and environment variable substitution
- `BacktestingEngine/strategy.py`: strategy abstraction and signal generators
- `BacktestingEngine/positionSizer.py`: position sizing implementations
- `BacktestingEngine/backtestEngine.py`: portfolio simulation, commissions, slippage, and exits
- `BacktestingEngine/performanceMetrics.py`: performance calculations and reporting
- `DataLoader/dataLoader.py`: input validation, parsing, retries, and logging
- `DataStorage/dataStorage.py`: PostgreSQL storage, pooling, indexing, and schema management
- `logging_config.py`: structured logging setup

## How to run

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Run the default backtest

```bash
python main.py
```

3. Run a different configuration

```bash
docker compose run --rm app python main.py --config config_volatility.yaml
```

4. Use a custom configuration file

```bash
cp config.yaml my_config.yaml
python main.py --config my_config.yaml
```

## Configuration

The main `config.yaml` file contains the core runtime settings:
- `backtest`: initial cash, commissions, slippage, stop-loss, take-profit, and selected sizing strategy
- `strategy`: strategy name and its parameters
- `data`: ticker and date range
- `database`: PostgreSQL connection settings and pool size
- `logging`: log level and file rotation settings

## Useful config variants

- `config_conservative.yaml`: fixed-shares sizing for simpler execution
- `config_kelly.yaml`: Kelly criterion sizing for adaptive risk management
- `config_volatility.yaml`: volatility-adjusted sizing for regime-aware trade sizing

## Testing

Run the test suite with:

```bash
python -m pytest -q
```

## Notes

- The engine logs warnings and audit-relevant events instead of relying on `print()` output
- Performance summaries are written to the log stream and can be reviewed in `logs/backtester.log`
- The configuration framework supports multiple backtests without code changes
- The storage layer gracefully handles missing or legacy schema elements
