"""Test progemi token api"""

import asyncio

from typing import List

from app.auth.schemas import ConnectedUser

from app.progemi_api.schemas import ProjectProgemi

from app.progemi_api.progemi_api_handler import ProgemiAPIHandler


async def test_token_api() -> None:
    """Test the Progemi API token retrieval."""

    TOKEN = "gw35W3tRrHHNRQTCkn7LIfnqZ7mC8KSzgQRWPelRGn-9C4XNqu0YWYJEewNyWHlZewStJJpJwQ4hR0V-7MuR1457wjR_"

    user_id: str = await ProgemiAPIHandler().get_user_id_from_token(token=TOKEN)

    connected_user = ConnectedUser(
        user_id=user_id,
        token=TOKEN,
        ip_client="127.0.0.1",
        idholding=1,
        idsociete=1,
        idagence=1,
    )

    projects: List[ProjectProgemi] = await ProgemiAPIHandler().get_user_project(
        connected_user=connected_user
    )

    for project in projects:
        print(project.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(test_token_api())
