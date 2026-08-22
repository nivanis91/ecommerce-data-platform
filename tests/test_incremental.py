import pandas as pd

from src.pipeline import ingest_table_idempotent


def test_incremental_load(monkeypatch):

    df = pd.DataFrame({
        "order_id": [101, 102],
        "updated_at": pd.to_datetime([
            "2026-08-21 10:00:00",
            "2026-08-21 11:00:00"
        ], utc=True)
    })

    # Mock database connection
    class FakeConnection:
        def close(self):
            pass

    monkeypatch.setattr(
        "src.pipeline.get_postgres_connection",
        lambda: FakeConnection()
    )

    # Mock existing BigQuery watermark
    monkeypatch.setattr(
        "src.pipeline.get_watermark",
        lambda table: "2026-08-21 09:00:00+00:00"
    )

    # Mock BigQuery merge
    monkeypatch.setattr(
        "src.pipeline.merge_dataframe_to_bigquery",
        lambda df, table, keys: None
    )

    # Fake extraction function
    def fake_extract(conn, watermark):
        assert watermark == "2026-08-21 09:00:00+00:00"
        return df

    # Capture the new watermark
    updated_watermark = {}

    def fake_update_watermark(table, watermark):
        updated_watermark["table"] = table
        updated_watermark["watermark"] = watermark

    monkeypatch.setattr(
        "src.pipeline.update_watermark",
        fake_update_watermark
    )

    ingest_table_idempotent(
        extract_function=fake_extract,
        bq_table="raw.orders",
        merge_keys=["order_id"],
        watermark_colum_name="updated_at"
    )

    assert updated_watermark["table"] == "raw.orders"
    assert updated_watermark["watermark"] == str(df['updated_at'].max())