"""
REST API endpoints for user management, message handling, and file uploads.

Includes:

- Add, update, list and delete users.
- Upload files.
- Get recent messages and delete them.
- Retrieve user configuration from request token.
- Track connected users via WebSocket manager.

"""

import asyncio
from typing import List

from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import JSONResponse

from ..configuration import LOGGER, MANAGER
from ..middleware.auth import AuthMiddleware
from ..models import Message, ApiUser
from ..models.schemas import (
    UserSchema,
    ShowUserSchema,
    MessageSchema,
    UserConnection
)
from ..utils.functions import add_user, update_user, save_file

v1_router = APIRouter()


@v1_router.post('/user', response_class=JSONResponse)
def adding_user(user_parameter: UserSchema) -> JSONResponse:
    """
    Add a new user to the database.

    Handles exceptions and logs any errors that may occur during creation.

    :param user_parameter: User data to be added.
    :return: JSON response indicating success or failure.
    """
    status_code = 200
    try:
        message = add_user(user_parameter)
    except Exception as e:
        message = f"There was a problem. msg {e}"
        status_code = 404
        LOGGER.error(message)

    return JSONResponse(content={"msg": message}, status_code=status_code)


@v1_router.post("/upload-files/")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or more files asynchronously.

    :param files: List of files to upload.
    :return: Dictionary with names of uploaded files.
    """
    tasks = [save_file(file) for file in files]
    results = await asyncio.gather(*tasks)
    return {"uploaded_files": results}


@v1_router.get("/connected-users")
async def get_connected_users() -> List[UserConnection]:
    """
    Get the list of currently connected WebSocket users.

    :return: List of user names wrapped in UserConnection schema.
    """
    users = MANAGER.get_connected_users()
    return [UserConnection(name=u) for u in users]


@v1_router.get("/user-info")
def get_user_conf(request: Request) -> JSONResponse:
    """
    Retrieve user configuration from the request's authentication token.

    :param request: HTTP request object containing headers and cookies.
    :return: JSON response with user configuration or 400 if not found.
    """
    config = AuthMiddleware(None).get_user_config(request)
    status = 200 if config else 400
    return JSONResponse(content=config or {}, status_code=status)


@v1_router.get("/users/", response_model=List[ShowUserSchema])
def user_listing():
    """
    List all users in the database.

    :return: List of users with limited (safe-to-expose) data.
    """
    users_ = ApiUser.select()
    return [ShowUserSchema.from_orm(usr_) for usr_ in users_]


@v1_router.get("/messages")
def get_messages(request: Request) -> List[MessageSchema]:
    """
    Retrieve the 10 most recent messages.

    Marks messages as "isMine=True" if sent by the requesting user.

    :param request: HTTP request used to determine current user.
    :return: List of MessageSchema objects sorted oldest to newest.
    """
    config = AuthMiddleware(None).get_user_config(request)
    messages = Message.select().order_by(Message.id.desc()).limit(10)
    listing_ = [MessageSchema.from_orm(msg) for msg in messages[::-1]]
    for m_ in listing_:
        if m_.user_id == config.get('preferred_username', ''):
            m_.isMine = True
    return listing_


@v1_router.put("/users/{user_id}", response_model=UserSchema)
def updating_user(user_id: str, user_update: UserSchema):
    """
    Update an existing user.

    :param user_id: ID of the user to update.
    :param user_update: Updated user data.
    :return: Updated user object or 404 if not found.
    """
    user_ = ApiUser.get_or_none(ApiUser.id == user_id)
    if not user_:
        return JSONResponse(status_code=404, content="User not found")

    user_updated = update_user(user_, user_update)
    return UserSchema.from_orm(user_updated)


@v1_router.delete("/users/{user_id}")
def delete_user(user_id: int):
    """
    Delete a user by ID.

    :param user_id: ID of the user to delete.
    :return: Success message or 404 if user not found.
    """
    user_ = ApiUser.get_or_none(ApiUser.id == user_id)
    if not user_:
        return JSONResponse(status_code=404, content="User not found")

    user_.delete_instance()
    return JSONResponse(status_code=200, content="User deleted")


@v1_router.delete("/messages")
def delete_messages():
    """
    Delete all chat messages from the database.

    :return: Confirmation message.
    """
    Message.delete().execute()
    return JSONResponse(status_code=200, content="Messages deleted")
