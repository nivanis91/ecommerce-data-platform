
import pandas as pd
from src.config.cities import CITIES
from src.ingestion.utils import retry_operation, should_retry_weather
import requests

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

import logging

logger = logging.getLogger(__name__)

def fetch_weather(latitude, longitude, start_date, end_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
        ],
        "timezone": "auto",
    }

    response = requests.get(
        BASE_URL, 
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def parse_weather(data, location):
    hourly = data["hourly"]

    df = pd.DataFrame(hourly)

    df["location"] = location
    df["timestamp"] = pd.to_datetime(df["time"])

    df = df.drop(columns=["time"])

    return df

def get_weather(city, start_date, end_date):
    data = fetch_weather(
        latitude=city["latitude"],
        longitude=city["longitude"],
        start_date=start_date,
        end_date=end_date,
    )

    return parse_weather(
        data=data,
        location=city["name"],
    )


if __name__ == "__main__":
    all_weather = pd.DataFrame()

    for city in CITIES:
        df = retry_operation(
            get_weather(
                city=city,
                start_date="2026-08-01",
                end_date="2026-08-12",
            ),
            should_retry_weather
        )

        all_weather = pd.concat([all_weather, df], ignore_index=True)

    logger.info(
        "Loaded %s rows into %s",
        len(all_weather),
        'raw.weather'
    )
