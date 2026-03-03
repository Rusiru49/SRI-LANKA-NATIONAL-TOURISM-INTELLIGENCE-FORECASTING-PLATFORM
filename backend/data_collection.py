import logging
import os
import requests
import pdfplumber
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import config

# configure module-level logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO
)
def generate_sample_data(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    countries: Optional[list[str]] = None,
    seed: Optional[int] = None,
) -> pd.DataFrame:
    """Create synthetic monthly arrival figures for a list of countries.

    Parameters are configurable to make the data deterministic and reusable
    for tests or demonstration purposes.

    Args:
        start: first month included (defaults to 2018-01-01)
        end: last month included (defaults to 2025-11-01)
        countries: list of country names; uses a built-in list if not supplied.
        seed: random seed for reproducibility.

    Returns:
        DataFrame with columns ['date','year','month','country',
        'arrivals','avg_temperature','rainfall_mm'] saved to
        :data:`config.PROCESSED_DATA_FILE`.
    """
    logger.info("Generating sample tourism data...")

    if seed is not None:
        np.random.seed(seed)

    if start is None:
        start = datetime(2018, 1, 1)
    if end is None:
        end = datetime(2025, 11, 1)

    dates = pd.date_range(start=start, end=end, freq="MS")

    if countries is None:
        countries = config.DEFAULT_COUNTRIES

    data: list[dict] = []

    for date in dates:
        month = date.month
        year = date.year

        # seasonality
        if month in [12, 1, 2, 3]:
            seasonal_factor = 1.8
        elif month in [5, 6, 7, 8, 9]:
            seasonal_factor = 0.6
        else:
            seasonal_factor = 1.0

        # covid / crisis / recovery
        if year == 2020 and month >= 3:
            covid_factor = 0.05
        elif year == 2020:
            covid_factor = 0.8
        elif year == 2021:
            covid_factor = 0.2 + (month / 12) * 0.3
        else:
            covid_factor = 1.0

        crisis_factor = 0.4 if year == 2022 else 1.0
        recovery_factor = (
            0.6 + (month / 24) if year == 2023 else 1.2 if year == 2024 else 1.0
        )

        for i, country in enumerate(countries):
            country_base = config.BASE_ARRIVALS * (1 - i * 0.05)
            arrivals = int(
                country_base
                * seasonal_factor
                * covid_factor
                * crisis_factor
                * recovery_factor
                * (0.8 + np.random.random() * 0.4)
            )
            data.append(
                {
                    "date": date,
                    "year": year,
                    "month": month,
                    "country": country,
                    "arrivals": max(arrivals, 0),
                }
            )

    df = pd.DataFrame(data)

    # add simplified weather
    df["avg_temperature"] = df["month"].apply(
        lambda m: 28 if m in [3, 4, 5] else 26 if m in [6, 7, 8] else 27
    )
    df["rainfall_mm"] = df["month"].apply(
        lambda m: 250 if m in [5, 10, 11] else 100 if m in [6, 9] else 50
    )

    output_file = Path(config.PROCESSED_DATA_FILE)
    df.to_csv(output_file, index=False)

    logger.info("Sample data generated: %s", output_file)
    logger.info("Total records: %d", len(df))
    logger.info("Date range: %s to %s", df["date"].min(), df["date"].max())

    return df

def scrape_sltda_pdfs() -> pd.DataFrame:
    """Placeholder for scraping SLTDA website for arrival tables.

    When the real endpoint is available the implementation should:
    1. download each PDF into ``config.RAW_DATA_DIR``
    2. call :func:`extract_pdf_tables` and clean/concatenate the results
    3. return a consolidated DataFrame with the same schema as the
       generated sample data, so downstream code remains unchanged.

    At present we fall back to synthetic data and log the activity.
    """
    logger.info("Attempting to scrape SLTDA data (stub). Using sample data.")
    # TODO: implement real scraping using requests/BeautifulSoup and
    #       update `extract_pdf_tables` to return a DataFrame.
    return generate_sample_data()

def extract_pdf_tables(pdf_path: str) -> list:
    """Return list of raw tables from a PDF using ``pdfplumber``.

    A later refactor could convert each table to a DataFrame and apply a
    schema transformation. Keeping the low-level list return value makes
    initial debugging easier.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            tables: list = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    logger.debug("page %d: %d tables", page.page_number, len(page_tables))
                    tables.extend(page_tables)
            return tables
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error extracting PDF %s: %s", pdf_path, exc)
        return []

def _get_raw_pdf_paths() -> list[Path]:
    """Return a list of Path objects for PDF files in the raw directory."""
    raw_dir = Path(config.RAW_DATA_DIR)
    return list(raw_dir.glob("*.pdf"))


def extract_all_pdfs_in_raw() -> None:
    """Walk through published PDFs and log the number of tables found.

    This function does not transform or save the contents; it is useful for
    sanity-checking the raw extraction step during development.
    """
    pdf_paths = _get_raw_pdf_paths()
    logger.info("Found %d PDF files in %s.", len(pdf_paths), config.RAW_DATA_DIR)
    for pdf_path in pdf_paths:
        logger.info("extracting tables from %s", pdf_path.name)
        tables = extract_pdf_tables(str(pdf_path))
        logger.info("%s contained %d tables", pdf_path.name, len(tables))
    logger.info("all pdfs extraction attempted.")

def fetch_weather_data(
    lat: float = 7.8731,
    lon: float = 80.7718,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    retries: int = 3,
) -> Optional[pd.DataFrame]:
    """Download daily temperature/precipitation from Open-Meteo.

    Args:
        lat: latitude of the location (default Sri Lanka centre).
        lon: longitude of the location.
        start_date: YYYY-MM-DD string; defaults to one year ago.
        end_date: YYYY-MM-DD string; defaults to today.
        retries: how many times to retry network requests.

    Returns:
        DataFrame on success, ``None`` on failure.
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    url = config.WEATHER_API_URL
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_mean,precipitation_sum",
        "timezone": "Asia/Colombo",
    }

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        resp = session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(data["daily"]["time"]),
                "temperature": data["daily"]["temperature_2m_mean"],
                "precipitation": data["daily"]["precipitation_sum"],
            }
        )
        logger.info("weather data fetched %s to %s (%d rows)", start_date, end_date, len(df))
        return df
    except Exception as exc:
        logger.error("Error fetching weather data: %s", exc)
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Collect or generate tourism data.")
    parser.add_argument("--generate-sample", action="store_true", help="Force generation of synthetic sample data")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("starting data collection module")
    extract_all_pdfs_in_raw()

    if args.generate_sample:
        df = generate_sample_data()
    else:
        df = scrape_sltda_pdfs()

    logger.info("data collection completed successfully")
    logger.info("data shape: %s", df.shape)
    logger.debug("sample records:\n%s", df.head())
    logger.info("data saved to: %s", config.PROCESSED_DATA_FILE)