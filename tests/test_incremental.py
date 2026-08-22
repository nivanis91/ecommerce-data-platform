import pandas as pd

from src.pipeline import ingest_table_idempotent

import pandas as pd
import pytest
from unittest.mock import Mock

from src.pipeline import ingest_table_idempotent


@pytest.fixture
def df():
    return pd.DataFrame({
        "order_id": [101, 102],
        "updated_at": pd.to_datetime([
            "2026-08-21 10:00:00",
            "2026-08-21 11:00:00"
        ], utc=True)
    })

@pytest.fixture
def empty_df():
    return pd.DataFrame({
        "order_id": [],
        "updated_at": pd.to_datetime([], utc=True)
    })

@pytest.fixture
def no_new_df():
    return pd.DataFrame({
        "order_id": [101, 102],
        "updated_at": pd.to_datetime([
            "2026-08-21 09:00:00",
            "2026-08-21 09:00:00"
        ], utc=True)
    })

@pytest.fixture
def fake_connection():
    class FakeConnection:
        def close(self):
            pass

    return FakeConnection()


@pytest.fixture
def fake_extract(df):
    def extract(conn, watermark):
        return df

    return extract

@pytest.fixture
def fake_extract_no_new(no_new_df):
    def extract(conn, watermark):
        return no_new_df

    return extract

@pytest.fixture
def fake_extract_empty(empty_df):
    def extract(conn, watermark):
        return empty_df

    return extract

@pytest.fixture
def updated_watermark():
    return {}


@pytest.fixture
def mock_pipeline(monkeypatch, fake_connection, updated_watermark):
    monkeypatch.setattr(
        "src.pipeline.get_postgres_connection",
        lambda: fake_connection
    )

    monkeypatch.setattr(
        "src.pipeline.merge_dataframe_to_bigquery",
        lambda df, table, keys: None
    )

    def fake_update_watermark(table, watermark):
        updated_watermark["table"] = table
        updated_watermark["watermark"] = watermark

    monkeypatch.setattr(
        "src.pipeline.update_watermark",
        fake_update_watermark
    )

def test_update_existing_watermark_when_new_rows_exist(
    df,
    fake_extract,
    updated_watermark,
    mock_pipeline,
    monkeypatch
):
    monkeypatch.setattr(
        "src.pipeline.get_watermark",
        lambda table: "2026-08-21 09:00:00+00:00"
    )

    ingest_table_idempotent(
        extract_function=fake_extract,
        bq_table="raw.orders",
        merge_keys=["order_id"],
        watermark_colum_name="updated_at"
    )

    assert updated_watermark["table"] == "raw.orders"
    assert updated_watermark["watermark"] == str(df["updated_at"].max())


def test_dont_update_existing_watermark_when_new_rows_match_watermark(
    no_new_df,
    fake_extract_no_new,
    updated_watermark,
    mock_pipeline,
    monkeypatch
):
    mock_update_watermark = Mock()

    monkeypatch.setattr(
        "src.pipeline.update_watermark",
        mock_update_watermark
    )
    monkeypatch.setattr(
        "src.pipeline.get_watermark",
        lambda table: "2026-08-21 09:00:00+00:00"
    )

    ingest_table_idempotent(
        extract_function=fake_extract_no_new,
        bq_table="raw.orders",
        merge_keys=["order_id"],
        watermark_colum_name="updated_at"
    )

    mock_update_watermark.assert_not_called()


def test_create_watermark_when_there_was_none(
    df,
    fake_extract,
    updated_watermark,
    mock_pipeline,
    monkeypatch
):
    monkeypatch.setattr(
        "src.pipeline.get_watermark",
        lambda table: None
    )

    ingest_table_idempotent(
        extract_function=fake_extract,
        bq_table="raw.orders",
        merge_keys=["order_id"],
        watermark_colum_name="updated_at"
    )

    assert updated_watermark["table"] == "raw.orders"
    assert updated_watermark["watermark"] == str(df["updated_at"].max())


def test_dont_update_watermark_when_df_is_empty(
    empty_df,
    fake_extract_empty,
    updated_watermark,
    mock_pipeline,
    monkeypatch
):
    mock_update_watermark = Mock()

    monkeypatch.setattr(
        "src.pipeline.update_watermark",
        mock_update_watermark
    )
    monkeypatch.setattr(
        "src.pipeline.get_watermark",
        lambda table: "2026-08-21 09:00:00+00:00"
    )

    ingest_table_idempotent(
        extract_function=fake_extract_empty,
        bq_table="raw.orders",
        merge_keys=["order_id"],
        watermark_colum_name="updated_at"
    )

    mock_update_watermark.assert_not_called()