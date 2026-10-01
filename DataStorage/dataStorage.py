"""
Data storage module with connection pooling and resilient schema management.

This module exposes a backward-compatible store_data() function while
providing a normalized and indexed schema for PostgreSQL storage.
"""

import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2 import pool
from psycopg2.extras import execute_values
from logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PostgresConfig:
    host: str
    database: str
    user: Optional[str]
    password: Optional[str]
    minconn: int = 1
    maxconn: int = 5


class DatabaseConnectionPool:
    def __init__(self, config: PostgresConfig):
        self.config = config
        self.pool: Optional[pool.SimpleConnectionPool] = None

    def initialize(self):
        if self.pool is None:
            logger.info(
                "Initializing PostgreSQL connection pool: %s-%s",
                self.config.minconn,
                self.config.maxconn,
            )
            self.pool = pool.SimpleConnectionPool(
                self.config.minconn,
                self.config.maxconn,
                host=self.config.host,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
            )

    def close(self):
        if self.pool:
            logger.info("Closing PostgreSQL connection pool")
            self.pool.closeall()
            self.pool = None

    @contextmanager
    def get_connection(self):
        if self.pool is None:
            self.initialize()

        if self.pool is None:
            raise RuntimeError("Connection pool failed to initialize")

        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)


class DataStorage:
    def __init__(self):
        load_dotenv()
        self.config = PostgresConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'stock_data'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            minconn=int(os.getenv('DB_MINCONN', 1)),
            maxconn=int(os.getenv('DB_MAXCONN', 5)),
        )
        self.pool = DatabaseConnectionPool(self.config)

    def initialize_schema(self):
        with self.pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        date DATE NOT NULL,
                        ticker VARCHAR(10) NOT NULL,
                        open NUMERIC(18, 6) NOT NULL,
                        high NUMERIC(18, 6) NOT NULL,
                        low NUMERIC(18, 6) NOT NULL,
                        close NUMERIC(18, 6) NOT NULL,
                        volume BIGINT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (date, ticker),
                        CHECK (open > 0 AND close > 0 AND volume >= 0),
                        CHECK (high >= low),
                        CHECK (high >= open AND high >= close),
                        CHECK (low <= open AND low <= close)
                    )
                """)

                # Handle legacy schemas by adding missing audit columns.
                cur.execute("""
                    ALTER TABLE stock_prices
                    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW(),
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW()
                """)

                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker
                    ON stock_prices(ticker)
                """)

                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_stock_prices_date
                    ON stock_prices(date)
                """)

                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker_date
                    ON stock_prices(ticker, date)
                """)

                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_stock_prices_date_ticker
                    ON stock_prices(date, ticker)
                """)

                conn.commit()
                logger.info("Schema verified and indexes created")

    def _prepare_data(self, data, ticker):
        prepared = []
        data = data.copy()
        data['ticker'] = ticker
        cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'ticker']
        if not all(col in data.columns for col in cols):
            raise ValueError("Input data must contain date/open/high/low/close/volume columns")

        data = data[cols]
        for row in data.itertuples(index=False, name=None):
            prepared.append(row)

        return prepared

    def store_data(self, data, ticker):
        if data is None or data.empty:
            logger.warning("No data to store for %s", ticker)
            return

        try:
            self.pool.initialize()
            self.initialize_schema()
        except Exception as exc:
            logger.warning(
                "Database initialization failed for %s (continuing without storage): %s",
                ticker,
                exc,
                exc_info=True,
            )
            return

        rows = self._prepare_data(data, ticker)
        if not rows:
            logger.warning("No prepared rows to store for %s", ticker)
            return

        try:
            with self.pool.get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        """
                            INSERT INTO stock_prices
                            (date, open, high, low, close, volume, ticker)
                            VALUES %s
                            ON CONFLICT (date, ticker) DO UPDATE SET
                                open = EXCLUDED.open,
                                high = EXCLUDED.high,
                                low = EXCLUDED.low,
                                close = EXCLUDED.close,
                                volume = EXCLUDED.volume,
                                updated_at = NOW()
                        """,
                        rows,
                    )
                    conn.commit()
                    logger.info("Stored %s rows for %s", len(rows), ticker)
        except Exception as exc:
            logger.warning(
                "Database storage failed for %s (continuing without storage): %s",
                ticker,
                exc,
                exc_info=True,
            )

    def close(self):
        self.pool.close()


def store_data(data, ticker):
    storage = DataStorage()
    try:
        storage.store_data(data, ticker)
    finally:
        storage.close()
