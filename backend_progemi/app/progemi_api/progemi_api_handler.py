"""PROGEMI API Handler Module"""

from typing import Dict, List, Optional

import httpx

from app.auth.schemas import ConnectedUser
from app.progemi_api.schemas import PackProgemi, ProjectProgemi

from app.progemi_api.exception import (
    InvalidToken,
    PacksError,
    ProjectError,
    UserTokenError,
)

from config.config import env_param

from config.logger_config import logger


class ProgemiAPIHandler:
    """Handler for interactions with the Progemi API."""

    @staticmethod
    def make_url(token: str, route: str) -> str:
        """Create the PROGEMI API URL for given token and route"""

        return f"{env_param.PROGEMI_API_BASE_URL}/{env_param.PROGEMI_API_VERSION}/apikey/{token}/{route}"

    async def get_user_packs(self, token: str) -> List[PackProgemi]:
        """
        Retrieve the List of packs from the Progemi API.

        Returns:
            List of PackProgemi objects.
        """

        try:
            url = self.make_url(token, "lots")

            async with httpx.AsyncClient() as client:
                response = await client.get(url)

                response.raise_for_status()

                packs_data = response.json()

                packs: List[PackProgemi] = [
                    PackProgemi(**pack) for pack in packs_data["lot"]
                ]

            logger.debug("PROGEMI API => ✅ Retrieved %d packs", len(packs))

            return packs

        except httpx.HTTPStatusError as e:
            if e.response.status_code == "403":
                logger.error("PROGEMI API => ❌ Invalid token")

                raise InvalidToken() from e

            logger.error(
                "PROGEMI API => ❌ Error retrieving packs: %s", e.response.text
            )

            raise PacksError(
                reason=f"HTTP error {e.response.status_code}: {e.response.text}"
            ) from e

    async def get_user_id_from_token(self, token: str) -> str:
        """
        Retrieve the user id from the Progemi API using the provided token.

        Args:
            token (str): The authentication token.

        Returns:
            str: The id of the user associated with the token.
        """

        try:
            url = self.make_url(token, "controletoken")

            async with httpx.AsyncClient() as client:
                response = await client.get(url)

                response.raise_for_status()

                response_json: Dict = response.json()

            user_id: Optional[str] = response_json.get("nomholding", None)

            logger.debug("PROGEMI API => ✅ Retrieved user ID: %s", user_id)

            if not user_id:
                logger.error("PROGEMI API => ❌ 'nomholding' not found in response")

                raise UserTokenError(reason="'nomholding' not found in response")

            return user_id

        except httpx.HTTPStatusError as e:
            if e.response.status_code == "403":
                logger.error("PROGEMI API => ❌ Invalid token")

                raise InvalidToken() from e

            logger.error(
                "PROGEMI API => ❌ Error retrieving user ID: %s", e.response.text
            )

            raise UserTokenError(
                reason=f"HTTP error {e.response.status_code}: {e.response.text}"
            ) from e

    async def get_user_project(
        self, connected_user: ConnectedUser
    ) -> List[ProjectProgemi]:
        """
        Retrieve the List of projects from the Progemi API.

        Args:
            token (str): The authentication token.
            user_id (str): The user ID to filter projects.

        Returns:
            List of ProjectProgemi objects.
        """

        try:
            url = self.make_url(connected_user.token, "lireprojetssansetude")

            params = {
                "idholding": connected_user.idholding,
                "idsociete": connected_user.idsociete,
                "idagence": connected_user.idagence,
            }

            async with httpx.AsyncClient() as client:
                response = await client.request("GET", url, json=params)

                response.raise_for_status()

                projects_data = response.json()

                projects: List[ProjectProgemi] = [
                    ProjectProgemi(**project) for project in projects_data["projets"]
                ]

            logger.debug("PROGEMI API => ✅ Retrieved %d projects", len(projects))

            return projects

        except httpx.HTTPStatusError as e:
            if e.response.status_code == "403":
                logger.error("PROGEMI API => ❌ Invalid token")

                raise InvalidToken() from e

            logger.error(
                "PROGEMI API => ❌ Error retrieving projects: %s", e.response.text
            )

            raise ProjectError(
                reason=f"HTTP error {e.response.status_code}: {e.response.text}"
            ) from e
