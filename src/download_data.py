import time
from pathlib import Path

import pandas as pd
import requests

LAT, LON = 40.64, 22.94             #Thessaloniki
YEARS = range(2019,2026)            #2019-2025

AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
AIR_VARS= ["pm10", "pm2_5", "nitrogen_dioxide", "ozone"]

WEATHER_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_VARS = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "surface_pressure", "precipitation" ]

def get_year(url, variables, year):
    params = {
        "latitude": LAT,
        "longitude": LON,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "hourly": ",".join(variables),
        "timezone": "Europe/Athens",
    }
    response = requests.get(url, params=params, timeout=120)
    data = response.json()
    if "hourly" not in data:
        print("Status:", response.status_code)
        print("Response:", response.text[:500])
        raise SystemExit(1)
    time.sleep(1)  # be polite to the free API
    return pd.DataFrame(data["hourly"])


def download(url, variables):
    frames = []
    for year in YEARS:
        print(f"{year}...")
        frames.append(get_year(url, variables, year))
    return pd.concat(frames, ignore_index = True)

if __name__=="__main__":
    print("Downloading air quality...")
    air = download(AIR_URL, AIR_VARS)
    print("Downloading weather...")
    weather = download(WEATHER_URL, WEATHER_VARS)

    df = air.merge(weather, on="time")
    Path("data").mkdir(exist_ok = True)
    df.to_csv("data/thessaloniki_hourly.csv", index=False)
    print(f"Saved{len(df):,}rows to data/thessaloniki_hourly.csv")