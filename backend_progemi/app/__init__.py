"""init app modules"""

__version__ = "0.1.0"

import os

import json

from contextlib import asynccontextmanager

from typing import AsyncIterator

from fastapi import FastAPI

from beanie import init_beanie

from motor.motor_asyncio import AsyncIOMotorClient

from app.user.schemas import ProposalFile, User

from config.config import env_param

from config.logger_config import logger


@asynccontextmanager
async def lifespan(app_lifespan: FastAPI) -> AsyncIterator[None]:
    """
    Init fastapi app with Beanie and MongoDB connection.
    """

    openapi_schema = app_lifespan.openapi()

    with open(
        os.path.join(os.path.dirname(__file__), "openapi.json"), "w", encoding="utf-8"
    ) as file:
        json.dump(openapi_schema, file, indent=2)

    logger.debug("APP => ✅ OpenAPI schema saved to openapi.json")

    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient(
            env_param.MONGO_DB_URI,
            maxPoolSize=200,
            minPoolSize=10,
            connectTimeoutMS=3_000,
            serverSelectionTimeoutMS=3_000,
            uuidRepresentation="standard",
        )

        await init_beanie(
            database=client[env_param.USER_DB_NAME],
            document_models=[User, ProposalFile],
        )

    except Exception as e:
        logger.error("APP => Error initializing MongoDB connection: %s", str(e))

    try:
        yield

    finally:
        try:
            await client.close()

        except Exception as e:
            logger.error("APP => Error closing MongoDB connection: %s", str(e))


def create_app() -> FastAPI:
    """Create fast api app with background sync"""

    app = FastAPI(lifespan=lifespan)

    return app
