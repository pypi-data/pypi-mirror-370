import os.path

from fastapi import UploadFile

from ..configuration import LOGGER, SAVE_FOLDER, MANAGER
from ..models import UserSchema, ApiUser


def add_user(user_: UserSchema) -> str:
    """
    This function adds a user to the database. It first checks if the user's
    city is unknown and attempts to fetch it using an external API.
    If the user does not already exist in the database,
    it creates a new user entry; otherwise, it returns a message
    indicating the user already exists.

    :param user_: An instance of UserSchema containing user details such as
        name, postal_code, and city.

    :return: A string message indicating whether the user was added to the
        database or already exists.
    """
    message = "Added user {}:{} to database."

    exist_user = ApiUser.get_or_none(**user_.model_dump())

    if not exist_user:
        new_user = ApiUser.get_or_create(**user_.model_dump())
        message = message.format(new_user.uid, new_user.name)
    else:
        message = 'The user already exists!'

    return message


def update_user(user_: ApiUser, user_update: UserSchema) -> ApiUser:
    """
    This function updates an existing ApiUser instance with new data provided
    in a UserSchema instance and returns the updated ApiUser

    :param user_: An instance of ApiUser representing the user to be updated.
    :param user_update:  An instance of UserSchema containing the new data
        for the user.

    :return: An updated ApiUser instance with the new data applied.
    """

    user_.update(**user_update.dict()).where(
        ApiUser.uid == user_.uid).execute()

    user_updated = ApiUser.get(ApiUser.uid == user_.uid)

    return user_updated


async def save_file(file: UploadFile):
    """
    Asynchronously saves an uploaded file to disk in chunks and notifies
    connected clients.

    The file is saved in the `SAVE_FOLDER` directory, and any spaces in the
    filename are replaced with hyphens. The file is written in append-binary
    mode in case it is uploaded in chunks. After saving, a broadcast message is
    sent to all connected WebSocket clients to notify them of the new file.

    :param file: The uploaded file to be saved (FastAPI's `UploadFile`).
    """
    des_ = os.path.join(
        SAVE_FOLDER,
        file.filename.replace(' ', '-'))
    LOGGER.debug(f"Saving file: {file.filename}")
    with open(des_, "ab") as f:
        while content := await file.read(1024):
            f.write(content)
    await MANAGER.broadcast(f"File attached: {file.filename} ")
    LOGGER.debug(f"Saved file: {file.filename}")
