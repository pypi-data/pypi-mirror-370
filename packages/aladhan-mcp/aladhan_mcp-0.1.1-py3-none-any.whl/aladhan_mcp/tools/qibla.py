import httpx
from ..utils import ALADHAN_BASE, text_json


def register_qibla_tools(server):
    @server.tool(
        name="get_qibla",
        description="Get Qibla direction (bearing, degrees) from latitude/longitude."
    )
    async def get_qibla(lat: float, lon: float) -> str:
        """Get Qibla direction from coordinates.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
        """
        url = f"{ALADHAN_BASE}/qibla/{lat}/{lon}"
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            payload = r.json()

        data = payload.get("data", {})
        direction = data.get("direction")
        if direction is not None:
            return text_json({"direction": direction})
        return text_json(payload)
