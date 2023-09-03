from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import requests
import json
import datetime
import requests


router = APIRouter()


@router.get("/oura/fetch", status_code=status.HTTP_200_OK)
async def fetch_oura_data(
    # api_key: str = "BOXNCJUEE4PSKBUW7I2UWC7FPCVRAYQU",
    access_token: str = "BOXNCJUEE4PSKBUW7I2UWC7FPCVRAYQU",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    try:
        # make the request to the Oura API
        if start_date is None:
            start_date = (datetime.datetime.now() -
                          datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        if end_date is None:
            end_date = (datetime.datetime.now().strftime('%Y-%m-%d'))

        url = "https://api.ouraring.com/v2/usercollection/sleep"
        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text,
            )

        data = json.JSONDecoder().decode(response.content.decode())

        for sleep_data in data['data']:
            # Convert all fields from seconds to hours/minutes/seconds
            #        Convert all fields from seconds to decimal minutes
            sleep_data['awake_time'] = sleep_data['awake_time'] / 60
            sleep_data['deep_sleep_duration'] = sleep_data['deep_sleep_duration'] / 60
            sleep_data['light_sleep_duration'] = sleep_data['light_sleep_duration'] / 60
            sleep_data['rem_sleep_duration'] = sleep_data['rem_sleep_duration'] / 60
            sleep_data['total_sleep_duration'] = sleep_data['total_sleep_duration'] / 3600
            sleep_data['time_in_bed'] = sleep_data['time_in_bed'] / 3600
            sleep_data['latency'] = sleep_data['latency'] / 60
            bedtime_start = datetime.datetime.fromisoformat(
                sleep_data['bedtime_start'])
            bedtime_end = datetime.datetime.fromisoformat(
                sleep_data['bedtime_start'])
            sleep_data['bedtime_start'] = bedtime_start.strftime('%H:%M')
            sleep_data['bedtime_end'] = bedtime_end.strftime('%H:%M')
            sleep_data.pop('heart_rate', None)
            sleep_data.pop('movement_30_sec', None)
            sleep_data.pop('sleep_phase_5_min', None)
            sleep_data.pop('low_battery_alert', None)
            sleep_data.pop('temperature_deviation', None)
            sleep_data.pop('readiness_score_delta', None)
            sleep_data.pop('sleep_algorithm_version', None)
            sleep_data.pop("hrv", None)
        return data
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


def seconds_to_hours_minutes_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}h {minutes}m {seconds}s"
