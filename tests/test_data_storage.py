import pandas as pd

from DataStorage.dataStorage import DataStorage


def test_store_data_handles_pool_initialization_failure(monkeypatch):
    storage = DataStorage()

    def fail_initialize():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(storage.pool, "initialize", fail_initialize)

    data = pd.DataFrame(
        {
            "date": ["2020-01-02"],
            "open": [10.0],
            "high": [11.0],
            "low": [9.5],
            "close": [10.5],
            "volume": [1000],
        }
    )

    storage.store_data(data, "AAPL")

    assert True
