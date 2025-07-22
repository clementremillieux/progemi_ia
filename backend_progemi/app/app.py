"""Create fast api app"""

import os

import traceback

import certifi

from fastapi import FastAPI, Request

from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from app import create_app

from app.user.router import router as user_router

from config.logger_config import logger

os.environ["SSL_CERT_FILE"] = certifi.where()

app: FastAPI = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)


@app.exception_handler(Exception)
async def full_traceback_exception_handler(_: Request, exc: Exception):
    """Handle unhandled exceptions and return a full traceback."""

    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    logger.exception("APP => Unhandled error: %s", exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "traceback": tb,
        },
    )
