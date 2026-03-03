# backend/test_data_collection.py
"""Quick sanity checks for the data_collection module."""

from backend import data_collection
import pandas as pd


def test_generate_sample_data():
    """Ensure sample data can be produced and matches expected structure."""
    df = data_collection.generate_sample_data(seed=42)
    assert isinstance(df, pd.DataFrame)
    # should have at least one record per country per month in range
    assert "country" in df.columns
    assert "arrivals" in df.columns
    assert not df.empty
    # deterministic with seed
    df2 = data_collection.generate_sample_data(seed=42)
    pd.testing.assert_frame_equal(df, df2)


def test_fetch_weather_data():
    """Invoke weather API; may return None if network unavailable."""
    df = data_collection.fetch_weather_data(retries=1)
    if df is not None:
        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "temperature" in df.columns


def test_extract_pdf_tables_no_files(tmp_path, monkeypatch):
    # create an empty directory and patch RAW_DATA_DIR to point there
    monkeypatch.setattr(data_collection.config, "RAW_DATA_DIR", str(tmp_path))
    paths = data_collection._get_raw_pdf_paths()
    assert isinstance(paths, list)
    assert paths == []
