from ..utils import ALADHAN_BASE, get_json, text_json


def register_date_conversion_tools(server):
    @server.tool(
        name="list_calculation_methods",
        description="List Aladhan calculation methods (id -> name, params)."
    )
    async def list_calculation_methods() -> str:
        from ..utils import cache_get, cache_put
        cache_key = "methods"
        payload = cache_get(cache_key, ttl_s=86400)
        if not payload:
            payload = await get_json(f"{ALADHAN_BASE}/methods")
            cache_put(cache_key, payload)
        return text_json(payload.get("data", payload))

    @server.tool(
        name="convert_gregorian_to_hijri",
        description="Convert Gregorian date to Hijri. Args: date (YYYY-MM-DD)."
    )
    async def convert_gregorian_to_hijri(date: str) -> str:
        """Convert Gregorian date to Hijri.
        
        Args:
            date: Gregorian date in YYYY-MM-DD format
        """
        date = str(date).strip()
        if not date:
            raise ValueError("Required: 'date' as YYYY-MM-DD")
        payload = await get_json(f"{ALADHAN_BASE}/gToH", params={"date": date})
        return text_json(payload.get("data", payload))

    @server.tool(
        name="convert_hijri_to_gregorian",
        description="Convert Hijri date to Gregorian. Args: date (DD-MM-YYYY)."
    )
    async def convert_hijri_to_gregorian(date: str) -> str:
        """Convert Hijri date to Gregorian.
        
        Args:
            date: Hijri date in DD-MM-YYYY format
        """
        date = str(date).strip()
        if not date:
            raise ValueError("Required: 'date' as DD-MM-YYYY")
        payload = await get_json(f"{ALADHAN_BASE}/hToG", params={"date": date})
        return text_json(payload.get("data", payload))
