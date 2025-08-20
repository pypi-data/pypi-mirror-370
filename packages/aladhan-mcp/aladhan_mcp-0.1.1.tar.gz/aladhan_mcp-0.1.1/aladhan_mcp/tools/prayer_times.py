import datetime as dt
from typing import Optional
import httpx
from ..utils import ALADHAN_BASE, get_json, text_json


def register_prayer_times_tools(server):
    @server.tool(
        name="get_prayer_times",
        description="Get daily prayer times by coordinates."
    )
    async def get_prayer_times(
        lat: float,
        lon: float,
        date: Optional[str] = None,
        method: Optional[int] = None,
        school: Optional[int] = None,
        timezone: Optional[str] = None,
        iso8601: Optional[bool] = None
    ) -> str:
        """Get daily prayer times by coordinates.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            date: Date in DD-MM-YYYY format (defaults to today)
            method: Prayer calculation method (0-23 or 99)
            school: Islamic school (0=Shafi, 1=Hanafi)
            timezone: IANA timezone (e.g., Asia/Singapore)
            iso8601: Return times in ISO-8601 format
        """
        if not date:
            today = dt.date.today()
            date = today.strftime("%d-%m-%Y")

        params = {
            "latitude": lat,
            "longitude": lon,
        }

        if school is not None:
            if school not in (0, 1):
                raise ValueError("school must be 0 (Shafi) or 1 (Hanafi)")
            params["school"] = school

        if method is not None:
            params["method"] = method

        if timezone:
            params["timezonestring"] = timezone

        if iso8601 is not None:
            params["iso8601"] = "true" if iso8601 else "false"

        url = f"{ALADHAN_BASE}/timings/{date}"

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        timings = payload.get("data", {}).get("timings", {})
        return text_json(timings)

    @server.tool(
        name="get_prayer_times_by_city",
        description="Get daily prayer times by city/country."
    )
    async def get_prayer_times_by_city(
        city: str,
        country: str,
        state: Optional[str] = None,
        date: Optional[str] = None,
        method: Optional[int] = None,
        school: Optional[int] = None,
        timezone: Optional[str] = None,
        iso8601: Optional[bool] = None
    ) -> str:
        """Get daily prayer times by city/country.
        
        Args:
            city: City name
            country: Country name or 2-letter ISO code
            state: State/province (optional)
            date: Date in DD-MM-YYYY format (defaults to today)
            method: Prayer calculation method (0-23 or 99)
            school: Islamic school (0=Shafi, 1=Hanafi)
            timezone: IANA timezone (e.g., Asia/Singapore)
            iso8601: Return times in ISO-8601 format
        """
        city = city.strip()
        country = country.strip()
        if not city or not country:
            raise ValueError("Both 'city' and 'country' are required")

        if not date:
            date = dt.date.today().strftime("%d-%m-%Y")

        params: dict[str, object] = {
            "city": city,
            "country": country,
        }
        if state:
            params["state"] = state

        if method is not None:
            params["method"] = method

        if school is not None:
            if school not in (0, 1):
                raise ValueError("school must be 0 (Shafi) or 1 (Hanafi)")
            params["school"] = school

        if timezone:
            params["timezonestring"] = timezone

        if iso8601 is not None:
            params["iso8601"] = "true" if iso8601 else "false"

        url = f"{ALADHAN_BASE}/timingsByCity/{date}"
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        timings = payload.get("data", {}).get("timings", {})
        return text_json(timings)

    @server.tool(
        name="get_next_prayer",
        description="Get the next prayer for given coordinates."
    )
    async def get_next_prayer(
        lat: float,
        lon: float,
        date: Optional[str] = None,
        method: Optional[int] = None,
        school: Optional[int] = None,
        timezone: Optional[str] = None,
        iso8601: Optional[bool] = None
    ) -> str:
        """Get the next prayer (name and time) for given coordinates.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            date: Date in DD-MM-YYYY format (defaults to today)
            method: Prayer calculation method (0-23 or 99)
            school: Islamic school (0=Shafi, 1=Hanafi)
            timezone: IANA timezone (e.g., Asia/Singapore)
            iso8601: Return times in ISO-8601 format
        """
        if not date:
            date = dt.date.today().strftime("%d-%m-%Y")

        params: dict[str, object] = {
            "latitude": lat,
            "longitude": lon,
        }

        if method is not None:
            params["method"] = method

        if school is not None:
            if school not in (0, 1):
                raise ValueError("school must be 0 (Shafi) or 1 (Hanafi)")
            params["school"] = school

        if timezone:
            params["timezonestring"] = timezone

        if iso8601 is not None:
            params["iso8601"] = "true" if iso8601 else "false"

        url = f"{ALADHAN_BASE}/nextPrayer/{date}"
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        data = payload.get("data", {})

        if data:
            return text_json(data)

        return text_json(payload)
