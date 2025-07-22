"""Basic JWT authentication example using FastAPI."""

from typing import List

from fastapi import Cookie, Depends, HTTPException

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.user.schemas import NewUserInput

from app.auth.schemas import ConnectedUser

from app.user.user_handler import UserHandler

from app.progemi_api.schemas import PackProgemi

from app.progemi_api.progemi_api_handler import ProgemiAPIHandler

from config.logger_config import logger

auth_scheme = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    access_token: str | None = Cookie(default=None),
    ip_client: str | None = Cookie(default=None),
    idholding: str | None = Cookie(default=None),
    idsociete: str | None = Cookie(default=None),
    idagence: str | None = Cookie(default=None),
) -> ConnectedUser:
    """Verify JWT token and return the payload."""

    token = credentials.credentials if credentials else access_token

    logger.info("Verifying token: %s", token)

    if not token:
        raise HTTPException(status_code=401, detail="Missing credentials")

    user_id: str = await ProgemiAPIHandler().get_user_id_from_token(token=token)

    all_ai_db_user_ids: List[str] = await UserHandler().get_all_user_ids()

    if user_id not in all_ai_db_user_ids:
        logger.info("User %s not found in AI DB, creating new user entry.", user_id)

        user_packs_progemi: List[
            PackProgemi
        ] = await ProgemiAPIHandler().get_user_packs(token=token)

        await UserHandler().create_user(
            new_user_params=NewUserInput(
                user_id=user_id, user_name=user_id, user_packs=user_packs_progemi
            )
        )

    return ConnectedUser(
        user_id=user_id,
        token=token,
        ip_client=ip_client,
        idholding=idholding,
        idsociete=idsociete,
        idagence=idagence,
    )
