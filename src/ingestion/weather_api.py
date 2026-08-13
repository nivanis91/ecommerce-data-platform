import requests
import pandas as pd


BASE_URL = "https://api.open-meteo.com/v1/forecast"


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

    response = requests.get(BASE_URL, params=params)

    response.raise_for_status()

    return response.json()


def parse_weather(data, location):
    hourly = data["hourly"]

    df = pd.DataFrame(hourly)

    df["location"] = location
    df["timestamp"] = pd.to_datetime(df["time"])

    df = df.drop(columns=["time"])

    return df


def get_weather(latitude, longitude, start_date, end_date, location):
    data = fetch_weather(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
    )

    return parse_weather(
        data=data,
        location=location,
    )


if __name__ == "__main__":
    df = get_weather(
        latitude=44.7866,
        longitude=20.4489,
        start_date="2026-08-01",
        end_date="2026-08-12",
        location="Belgrade",
    )
    
    print(df.head())
    print(f"Rows: {len(df)}")