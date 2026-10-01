"""
Data loader for the backtesting engine.

This module fetches historical OHLCV data from Yahoo Finance, validates
inputs, and retries transient network failures.
"""

import time
from typing import Optional

import pandas as pd
import yfinance as yf

from logging_config import get_logger

logger = get_logger(__name__)


def load_data(
    ticker: str,
    start_date: str,
    end_date: str,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> pd.DataFrame:
    """
    Load historical OHLCV data for a stock ticker.

    Args:
        ticker: Stock ticker symbol.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        retries: Number of retry attempts when data cannot be loaded.
        retry_delay: Seconds to wait between retries.

    Returns:
        A pandas DataFrame containing OHLCV data.

    Raises:
        ValueError: If ticker or dates are invalid, or if data cannot be loaded.
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker symbol must be a non-empty string")

    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    except Exception as exc:
        raise ValueError("Invalid date format. Use YYYY-MM-DD") from exc

    if start >= end:
        raise ValueError("start_date must be before end_date")

    for attempt in range(1, retries + 1):
        data = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
        )

        if not data.empty:
            logger.info("Loaded %s rows for %s", len(data), ticker)
            return data

        logger.warning(
            "Attempt %s/%s failed to load data for %s",
            attempt,
            retries,
            ticker,
        )
        time.sleep(retry_delay)

    logger.error(
        "Failed to fetch data for %s after %s retries",
        ticker,
        retries,
    )
    raise ValueError(f"Failed to fetch data for {ticker}")

