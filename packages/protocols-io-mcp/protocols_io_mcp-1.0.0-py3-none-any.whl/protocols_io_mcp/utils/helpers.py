import os
import httpx
from typing import Literal, Any
from dotenv import load_dotenv
load_dotenv()

PROTOCOLS_IO_CLIENT_ACCESS_TOKEN = os.getenv("PROTOCOLS_IO_CLIENT_ACCESS_TOKEN")
PROTOCOLS_IO_API_URL = "https://www.protocols.io/api"

async def access_protocols_io_resource(method: Literal["GET", "POST", "PUT", "DELETE"], path: str, data: dict = None) -> dict[str, Any]:
    """Access protocols.io API with specified method and path."""
    headers = {
        "Authorization": f"Bearer {PROTOCOLS_IO_CLIENT_ACCESS_TOKEN}"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(method, f"{PROTOCOLS_IO_API_URL}{path}", json=data, headers=headers)
        return response.json()