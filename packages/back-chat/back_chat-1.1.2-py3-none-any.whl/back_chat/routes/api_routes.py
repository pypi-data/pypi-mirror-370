from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..configuration import DATABASE
from ..configuration import __version__

api_router = APIRouter()


@api_router.get("/health")
def health() -> JSONResponse:
    """
    Health check endpoint.

    Returns the current application version to confirm that the API is up and
    running.

    :return: JSON response containing the app version.
    """
    status_code = 200
    return JSONResponse(
        content={'version': __version__},
        status_code=status_code
    )


@api_router.on_event("shutdown")
def close_db():
    """
    Application shutdown event handler.

    Ensures that the database connection is properly closed
    when the FastAPI application stops.
    """
    if not DATABASE.is_closed():
        DATABASE.close()
