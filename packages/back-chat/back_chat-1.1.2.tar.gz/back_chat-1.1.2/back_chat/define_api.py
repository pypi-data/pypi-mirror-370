"""
Defines and initializes the FastAPI application, including route registration
and middleware setup.

This module serves as the main entry point for assembling the API structure
and exposing the application instance for use with ASGI servers.
"""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .configuration import (__version__, DATABASE, CORS_ORIGINS,
                            RABBITMQ_MANAGER, LOGGER)
from .middleware.auth import AuthMiddleware
from .models import Message, UserConf, ApiUser
from .routes import api_router, v1_router, ws_router

APP = FastAPI(
    title="REST API WITH EXAMPLES",
    summary="REST API WITH EXAMPLES",
    version=__version__
)


APP.include_router(
    router=api_router,
    prefix='/api',
    tags=["Service 1: API endpoints"]
)


APP.include_router(
    router=v1_router,
    prefix='/v1',
    tags=["Service 2: v1 endpoints"]
)

APP.include_router(
    router=ws_router,
    prefix='/ws',
    tags=["Service 3: web socket"]
)


# APP.add_middleware(AuthMiddleware)

APP.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE.connect()
DATABASE.create_tables([Message, UserConf, ApiUser])


# @APP.on_event("startup")
# async def startup_event():
#     try:
#         connected = await RABBITMQ_MANAGER.connect()
#     except Exception as e:
#         LOGGER.error(f"Connection error with RabbitMQ: {e}")
#         connected = False
#
#     if connected:
#         asyncio.create_task(
#             RABBITMQ_MANAGER.consume_messages_from_exchange("notifications")
#         )
