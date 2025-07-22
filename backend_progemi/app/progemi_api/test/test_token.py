"""Test progemi token api"""

import asyncio

from app.progemi_api.progemi_api_handler import ProgemiAPIHandler


async def test_token_api() -> None:
    """Test the Progemi API token retrieval."""

    TOKEN = "gw35W3tRrHHNRQTCkn7LIfnqZ7mC8KSzgQRWPelRGn-9C4XNqu0YWYJEewNyWHlZewStJJpJwQ4hR0V-7MuR1457wjR_"

    user_id: str = await ProgemiAPIHandler().get_user_id_from_token(token=TOKEN)

    print(f"User ID: {user_id}")


if __name__ == "__main__":
    asyncio.run(test_token_api())
