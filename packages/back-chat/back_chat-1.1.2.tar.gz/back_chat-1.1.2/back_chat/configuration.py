"""
Handles application configuration, including environment variable parsing,
settings management, and shared constants.

This module centralizes configuration logic to provide consistent and reusable
settings across the backend.
"""

import configparser
import os

from keycloak import KeycloakOpenID
from peewee import SqliteDatabase

from .services import ConnectionManager, RabbitMQManager
from .utils.logger_api import LoggerApi

__version__ = "1.1.2"

LOGGER = LoggerApi("back_chat")

conf_file = os.getenv('CONF_FILE', './conf/config.cfg')

config = configparser.ConfigParser()
config.read(conf_file)

API_IP = config.get('conf', "api_ip", fallback='0.0.0.0')
API_PORT = int(config.get('conf', "api_port", fallback='8000'))

DATABASE_NAME = config.get('conf', "DATABASE_NAME", fallback="my_database.db")

SAVE_FOLDER = config.get('conf', 'SAVE_FOLDER', fallback='./save')
MINUTES_REFRESH_CONF = config.getint('conf', "minutes_refresh_conf",
                                     fallback=5)
cors_ = config.get('conf', "cors_origins", fallback='').split(',')
CORS_ORIGINS = [c_ for c_ in cors_ if c_ != '']

KEYCLOAK_URL = config.get('keycloak', 'keycloak_url', fallback=None)

CLIENT_NAME = config.get('keycloak', 'client_name', fallback=None)
CLIENT_SECRET = os.getenv('CLIENT_SECRET', None)
REALM = config.get('keycloak', 'realm', fallback=None)

KEYCLOAK_OPENID = None

if None not in [KEYCLOAK_URL]:
    KEYCLOAK_OPENID = KeycloakOpenID(
        server_url=KEYCLOAK_URL,
        client_id=CLIENT_NAME,
        realm_name=REALM,
    )

DATABASE = SqliteDatabase(DATABASE_NAME)

MANAGER = ConnectionManager()

RABBITMQ_URL = config.get('rabbitmq', 'rabbitmq_url', fallback=None)
QUEUE_NAME = config.get('rabbitmq', 'queue_name', fallback='qn')
EXCHANGE_NAME = config.get('rabbitmq', 'exchange_name',
                           fallback='notifications')
RABBITMQ_MANAGER = RabbitMQManager(RABBITMQ_URL, MANAGER, logger=LOGGER)


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "back_chat.utils.logger_api.ColoredFormatter",
            "format": LOGGER.msg_format,
            "datefmt": LOGGER.datetime_format,
        },
        "filefrmt": {
            "format": LOGGER.msg_format,
            "datefmt": LOGGER.datetime_format,
        },

    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
        "file": {
            "()": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "filefrmt",
            "level": "DEBUG",
            "filename": LOGGER.file_name,
            "when": "midnight",
            "interval": 1,
            "backupCount": 4,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
        "uvicorn.error": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}