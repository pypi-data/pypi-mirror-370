from typing import Optional
import httpx
from ..utils import ALADHAN_BASE, get_json, text_json


def register_calendar_tools(server):
    @server.tool(
        name="get_hijri_calendar_by_city",
        description="Get Hijri month calendar by city/country."
    )
    async def get_hijri_calendar_by_city(
        year: int,
        month: int,
        city: str,
        country: str,
        state: Optional[str] = None,
        method: Optional[int] = None,
        school: Optional[int] = None,
        timezone: Optional[str] = None,
        iso8601: Optional[bool] = None,
        latitudeAdjustmentMethod: Optional[int] = None,
        calendarMethod: Optional[str] = None,
        midnightMode: Optional[int] = None,
        adjustment: Optional[int] = None
    ) -> str:
        """Get Hijri month calendar by city/country.
        
        Args:
            year: Hijri year (e.g., 1446)
            month: Hijri month (1-12)
            city: City name
            country: Country name or 2-letter ISO code
            state: State/province (optional)
            method: Prayer calculation method (0-23 or 99)
            school: Islamic school (0=Shafi, 1=Hanafi)
            timezone: IANA timezone (e.g., Asia/Singapore)
            iso8601: Return times in ISO-8601 format
            latitudeAdjustmentMethod: Latitude adjustment method (1-3)
            calendarMethod: Calendar calculation method (HJCoSA|UAQ|DIYANET|MATHEMATICAL)
            midnightMode: Midnight calculation mode (0-1)
            adjustment: Time adjustment in minutes
        """
        city = city.strip()
        country = country.strip()
        if not city or not country:
            raise ValueError("Both 'city' and 'country' are required")

        params: dict[str, object] = {"city": city, "country": country}
        if state:
            params["state"] = state
        if method is not None:
            params["method"] = method
        if school is not None:
            if school not in (0, 1):
                raise ValueError("school must be 0 or 1")
            params["school"] = school
        if timezone:
            params["timezonestring"] = timezone
        if latitudeAdjustmentMethod is not None:
            if latitudeAdjustmentMethod not in (1, 2, 3):
                raise ValueError("latitudeAdjustmentMethod must be 1..3")
            params["latitudeAdjustmentMethod"] = latitudeAdjustmentMethod
        if calendarMethod:
            if calendarMethod not in ("HJCoSA", "UAQ", "DIYANET", "MATHEMATICAL"):
                raise ValueError("calendarMethod must be HJCoSA, UAQ, DIYANET, or MATHEMATICAL")
            params["calendarMethod"] = calendarMethod
        if midnightMode is not None:
            if midnightMode not in (0, 1):
                raise ValueError("midnightMode must be 0 or 1")
            params["midnightMode"] = midnightMode
        if iso8601 is not None:
            params["iso8601"] = "true" if iso8601 else "false"
        if adjustment is not None:
            params["adjustment"] = adjustment

        url = f"{ALADHAN_BASE}/hijriCalendarByCity/{year}/{month}"
        payload = await get_json(url, params=params, timeout=20)
        return text_json(payload.get("data", payload))

    @server.tool(
        name="get_hijri_calendar",
        description="Get prayer times for a Hijri month by coordinates."
    )
    async def get_hijri_calendar(
        year: int,
        month: int,
        lat: float,
        lon: float,
        method: Optional[int] = None,
        school: Optional[int] = None,
        midnightMode: Optional[int] = None,
        timezone: Optional[str] = None,
        latitudeAdjustmentMethod: Optional[int] = None,
        calendarMethod: Optional[str] = None,
        iso8601: Optional[bool] = None,
        adjustment: Optional[int] = None
    ) -> str:
        """Get prayer times for a Hijri month by coordinates.
        
        Args:
            year: Hijri year (e.g., 1446)
            month: Hijri month (1-12)
            lat: Latitude coordinate
            lon: Longitude coordinate
            method: Prayer calculation method (0-23 or 99)
            school: Islamic school (0=Shafi, 1=Hanafi)
            midnightMode: Midnight calculation mode (0-1)
            timezone: IANA timezone (e.g., Asia/Singapore)
            latitudeAdjustmentMethod: Latitude adjustment method (1-3)
            calendarMethod: Calendar calculation method (HJCoSA|UAQ|DIYANET|MATHEMATICAL)
            iso8601: Return times in ISO-8601 format
            adjustment: Time adjustment in minutes
        """
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

        if midnightMode is not None:
            if midnightMode not in (0, 1):
                raise ValueError("midnightMode must be 0 or 1")
            params["midnightMode"] = midnightMode

        if timezone:
            params["timezonestring"] = timezone

        if latitudeAdjustmentMethod is not None:
            if latitudeAdjustmentMethod not in (1, 2, 3):
                raise ValueError("latitudeAdjustmentMethod must be 1, 2, or 3")
            params["latitudeAdjustmentMethod"] = latitudeAdjustmentMethod

        if calendarMethod:
            if calendarMethod not in ("HJCoSA", "UAQ", "DIYANET", "MATHEMATICAL"):
                raise ValueError("calendarMethod must be HJCoSA, UAQ, DIYANET, or MATHEMATICAL")
            params["calendarMethod"] = calendarMethod

        if iso8601 is not None:
            params["iso8601"] = "true" if iso8601 else "false"

        if adjustment is not None:
            params["adjustment"] = adjustment

        url = f"{ALADHAN_BASE}/hijriCalendar/{year}/{month}"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        data = payload.get("data", [])
        return text_json(data if data else payload)

    @server.tool(
        name="get_monthly_calendar",
        description="Get prayer times for a Gregorian month by coordinates."
    )
    async def get_monthly_calendar(
        year: int,
        month: int,
        lat: float,
        lon: float,
        method: Optional[int] = None,
        school: Optional[int] = None,
        midnightMode: Optional[int] = None,
        timezone: Optional[str] = None,
        latitudeAdjustmentMethod: Optional[int] = None,
        shafaq: Optional[str] = None,
        tune: Optional[str] = None,
        iso8601: Optional[bool] = None,
        adjustment: Optional[int] = None
    ) -> str:
        """Get prayer times for a Gregorian month by coordinates.
        
        Args:
            year: Gregorian year (e.g., 2025)
            month: Gregorian month (1-12)
            lat: Latitude coordinate
            lon: Longitude coordinate
            method: Prayer calculation method (0-23 or 99)
            school: Islamic school (0=Shafi, 1=Hanafi)
            midnightMode: Midnight calculation mode (0-1)
            timezone: IANA timezone (e.g., Asia/Singapore)
            latitudeAdjustmentMethod: Latitude adjustment method (1-3)
            shafaq: Shafaq type (general|ahmer|abyad)
            tune: Comma-separated minute offsets for timings
            iso8601: Return times in ISO-8601 format
            adjustment: Time adjustment in minutes
        """
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

        if midnightMode is not None:
            if midnightMode not in (0, 1):
                raise ValueError("midnightMode must be 0 or 1")
            params["midnightMode"] = midnightMode

        if timezone:
            params["timezonestring"] = timezone

        if latitudeAdjustmentMethod is not None:
            if latitudeAdjustmentMethod not in (1, 2, 3):
                raise ValueError("latitudeAdjustmentMethod must be 1, 2, or 3")
            params["latitudeAdjustmentMethod"] = latitudeAdjustmentMethod

        if shafaq:
            if shafaq not in ("general", "ahmer", "abyad"):
                raise ValueError("shafaq must be general, ahmer, or abyad")
            params["shafaq"] = shafaq

        if tune:
            params["tune"] = tune

        if iso8601 is not None:
            params["iso8601"] = "true" if iso8601 else "false"

        if adjustment is not None:
            params["adjustment"] = adjustment

        url = f"{ALADHAN_BASE}/calendar/{year}/{month}"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        data = payload.get("data", [])
        return text_json(data if data else payload)

    @server.tool(
        name="get_monthly_calendar_by_city",
        description="Get prayer times for a Gregorian month by city/country."
    )
    async def get_monthly_calendar_by_city(
        year: int,
        month: int,
        city: str,
        country: str,
        state: Optional[str] = None,
        method: Optional[int] = None,
        school: Optional[int] = None,
        midnightMode: Optional[int] = None,
        timezone: Optional[str] = None,
        latitudeAdjustmentMethod: Optional[int] = None,
        shafaq: Optional[str] = None,
        tune: Optional[str] = None,
        iso8601: Optional[bool] = None,
        adjustment: Optional[int] = None,
        x7xapikey: Optional[str] = None
    ) -> str:
        """Get prayer times for a Gregorian month by city/country.
        
        Args:
            year: Gregorian year (e.g., 2025)
            month: Gregorian month (1-12)
            city: City name
            country: Country name or 2-letter ISO code
            state: State/province (optional)
            method: Prayer calculation method (0-23 or 99)
            school: Islamic school (0=Shafi, 1=Hanafi)
            midnightMode: Midnight calculation mode (0-1)
            timezone: IANA timezone (e.g., Asia/Singapore)
            latitudeAdjustmentMethod: Latitude adjustment method (1-3)
            shafaq: Shafaq type (general|ahmer|abyad)
            tune: Comma-separated minute offsets for timings
            iso8601: Return times in ISO-8601 format
            adjustment: Time adjustment in minutes
            x7xapikey: API key for premium features
        """
        city = city.strip()
        country = country.strip()
        if not city or not country:
            raise ValueError("Both 'city' and 'country' are required")

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

        if midnightMode is not None:
            if midnightMode not in (0, 1):
                raise ValueError("midnightMode must be 0 or 1")
            params["midnightMode"] = midnightMode

        if timezone:
            params["timezonestring"] = timezone

        if latitudeAdjustmentMethod is not None:
            if latitudeAdjustmentMethod not in (1, 2, 3):
                raise ValueError("latitudeAdjustmentMethod must be 1, 2, or 3")
            params["latitudeAdjustmentMethod"] = latitudeAdjustmentMethod

        if shafaq:
            if shafaq not in ("general", "ahmer", "abyad"):
                raise ValueError("shafaq must be general, ahmer, or abyad")
            params["shafaq"] = shafaq

        if tune:
            params["tune"] = tune

        if iso8601 is not None:
            params["iso8601"] = "true" if iso8601 else "false"

        if adjustment is not None:
            params["adjustment"] = adjustment

        if x7xapikey:
            params["x7xapikey"] = x7xapikey

        url = f"{ALADHAN_BASE}/calendarByCity/{year}/{month}"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        data = payload.get("data", [])
        return text_json(data if data else payload)
