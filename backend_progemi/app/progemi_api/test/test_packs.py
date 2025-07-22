"""Test progemi token api"""

import asyncio

from typing import List

from app.progemi_api.schemas import PackProgemi

from app.progemi_api.progemi_api_handler import ProgemiAPIHandler


async def test_token_api() -> None:
    """Test the Progemi API token retrieval."""

    TOKEN = "gw35W3tRrHHNRQTCkn7LIfnqZ7mC8KSzgQRWPelRGn-9C4XNqu0YWYJEewNyWHlZewStJJpJwQ4hR0V-7MuR1457wjR_"

    packs: List[PackProgemi] = await ProgemiAPIHandler().get_packs(token=TOKEN)

    for pack in packs:
        print(pack.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(test_token_api())
